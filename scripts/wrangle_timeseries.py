#!/usr/bin/env python

import csv
from collections import defaultdict
import json
from pathlib import Path
import re
from sys import stderr

SRC_PATH = Path('data/fused/jhcsse_normalized.csv')
LOOKUPS_PATH = Path('data/lookups/fips.csv')
DEST_PATH = Path('data/wrangled/timeseries.csv')

MAX_DATE = '2020-03-22'


def _load_src_data():
    data = []
    with open(SRC_PATH) as ins:
        for d in csv.DictReader(ins):
            if d['country_region'] == 'US':
                try:
                    d['confirmed'] = int(d['confirmed']) if d['confirmed'] else 0
                    d['deaths'] = int(d['deaths']) if d['deaths'] else 0
                except Exception as e:
                    import pdb; pdb.set_trace()
                    raise e
                else:
                    data.append(d)

    return data



def extract_timeseries_by_state(state_abbrev, state_name, indata):
    series = []
    for i in indata:
        if (i['province_state'] == state_name
                                              or re.search(f', *{state_abbrev}$', i['province_state'])
                                              and i['country_region'] == 'US'):
            d = {
                'id': state_abbrev,
                'date': i['date'],
                'confirmed': i['confirmed'],
                'deaths': i['deaths'],
            }
            series.append(d)

    series = sorted(series, key=lambda d: d['date'])
    return series



def sum_timeseries(series):
    """groups multiple days in a state into single date summations"""
    _id = series[0]['id']
    dategroups = defaultdict(lambda: {'confirmed': 0, 'deaths': 0})
    for s in series:
        sdate = s['date']
        if sdate <= MAX_DATE:
            dategroups[sdate]['confirmed'] += s['confirmed']
            dategroups[sdate]['deaths'] += s['deaths']

    outdata = [{'id': _id, 'date': k, 'confirmed': v['confirmed'], 'deaths': v['deaths']} for k, v in dategroups.items()]
    return sorted(outdata, key=lambda d: d['date'])

def main():
    DEST_PATH.parent.mkdir(exist_ok=True, parents=True)
    srcdata = _load_src_data()
    lookups = list(csv.DictReader(LOOKUPS_PATH.open()))

    with open(DEST_PATH, 'w') as dest:
        outs = csv.DictWriter(dest, fieldnames=['id', 'date', 'confirmed', 'deaths'])
        outs.writeheader()

        for s in lookups:
            _x = extract_timeseries_by_state(s['postal_code'], s['full_name'], srcdata)
            _series = sum_timeseries(_x)
            outs.writerows(_series)

    stderr.write(f"Wrote {DEST_PATH.stat().st_size} chars to {DEST_PATH}\n")


if __name__ == '__main__':
    main()
