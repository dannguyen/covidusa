#!/usr/bin/env python

import csv
from collections import defaultdict
from datetime import date, timedelta
import json
from pathlib import Path
import re
from sys import stderr

SRC_PATH = Path('data/fused/jhcsse_normalized.csv')
LOOKUPS_PATH = Path('data/lookups/fips.csv')
DEST_PATH = Path('data/wrangled/state_summaries.json')


def _date_daysago(dt, days):
    return (date.fromisoformat(dt) - timedelta(days=days)).isoformat()

def _daysdiff(dy, dx):
    return (date.fromisoformat(dy) - date.fromisoformat(dx)).days



def _load_src_data():
    data = []
    with open(SRC_PATH) as ins:
        for d in csv.DictReader(ins):
            if d['country_region'] == 'US':
                d['confirmed'] = int(d['confirmed'])
                d['deaths'] = int(d['deaths'])
                data.append(d)
    return data


def extract_states_metas():
    meta = {}
    statelookups = list(csv.DictReader(LOOKUPS_PATH.open()))
    for s in statelookups:
        o = {'state': {}}
        o['state']['postal_code'] = s['postal_code']
        o['state']['name'] = s['full_name']
        o['state']['fips'] = s['fips']

        meta[s['postal_code']] = o
    return meta


def extract_state_series(state_abbrev, state_name, indata):
    data = {}
    series = [d for d in indata if d['province_state'] == state_name
                                      or re.search(f', *{state_abbrev}$', d['province_state'])
                                      and d['country_region'] == 'US']
    series = sorted(series, key=lambda d: d['date'])
    #print(f"state: {state_abbrev}, series count: {len(series)}")
    return series


def wrangle_state_series(series):
    outdata = {}

    dategroups = defaultdict(lambda: {'confirmed': 0, 'deaths': 0})
    for s in series:
        sdate = s['date']
        dategroups[sdate]['confirmed'] += s['confirmed']
        dategroups[sdate]['deaths'] += s['deaths']

    dates = sorted(dategroups.keys())

    # get current date
    zdate = dates[-1]
    z = dategroups[zdate]
    outdata['latest'] = {'date': zdate, 'confirmed': int(z['confirmed']), 'deaths': int(z['deaths'])}

    # get first day confirmed
    fdate = next((dt for dt in dates if dategroups[dt]['confirmed'] > 0), None)
    if fdate:
        fd = dategroups[fdate]
        daysago = _daysdiff(zdate, fdate)
        # fd_ctchange = z['confirmed'] - fd['confirmed']
        # fd_ptchange = round(100.0 * fd_ctchange / fd['confirmed'], 1)
        outdata['first'] = {'date': fdate, 'days_ago': daysago,
                            'confirmed': fd['confirmed'], 'deaths': fd['deaths'], }
                            # 'confirmed_count_change': fd_ctchange, 'confirmed_pct_change': fd_ptchange}

    else:
        daysago = 0
        outdata['first'] = {}


    outdata['days_ago'] = daydict = {}
    for dx in [1, 7, 14]:
        if daysago >= dx:
            xdate = _date_daysago(zdate, dx)
            xd = dategroups[xdate]
            x_ctchange = z['confirmed'] - xd['confirmed']
            x_ptchange = round(100.0 * x_ctchange / xd['confirmed'], 1)
            daydict[dx] = {'date': xdate,  'days_ago': dx,
                                'confirmed': xd['confirmed'],
                                'confirmed_count_change': x_ctchange, 'confirmed_pct_change': x_ptchange}
        else:
            daydict[dx] = {}


    return outdata


def main():
    DEST_PATH.parent.mkdir(exist_ok=True, parents=True)
    srcdata = _load_src_data()
    outdata = extract_states_metas()

    for state_ab, sdict in outdata.items():
        _series = extract_state_series(state_ab, sdict['state']['name'], srcdata)
        sdata = wrangle_state_series(_series)
        sdict.update(sdata)


    outtext = json.dumps(outdata, indent=2)
    DEST_PATH.write_text(outtext)
    stderr.write(f"Wrote {len(outtext)} chars to {DEST_PATH}\n")


if __name__ == '__main__':
    main()
