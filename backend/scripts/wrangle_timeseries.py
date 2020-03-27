#!/usr/bin/env python

import csv
from collections import defaultdict
import json
from pathlib import Path
import re
from sys import stderr

SRC_PATH = Path('backend/data/fused/jhcsse_normalized.csv')
LOOKUPS_PATH = Path('backend/data/lookups/fips.csv')
DEST_PATH = Path('backend/data/wrangled/timeseries.csv')

MAX_DATE = '2020-03-22'

HEADERS = ('id', 'date', 'confirmed', 'deaths', 'confirmed_diff', 'confirmed_diff_pct', 'deaths_diff', 'deaths_diff_pct')

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

def agg_state_series(series):
    """
    series is a list of rows for a single given state. assumed to be sorted by date, ascending order
    """
    for i, row in enumerate(series):
        if i < 1:
            row['confirmed_diff'] = row['deaths_diff'] = 0
        else:
            q = series[i-1]
            row['confirmed_diff'] = row['confirmed'] - q['confirmed']
            row['confirmed_diff_pct'] = round(100.0 * row['confirmed_diff'] / q['confirmed'], 1) if q['confirmed'] > 0 else None
            row['deaths_diff'] = row['deaths'] - q['deaths']
            row['deaths_diff_pct'] = round(100.0 * row['deaths_diff'] / q['deaths'], 1) if q['deaths'] > 0 else None

    return series




def main():
    DEST_PATH.parent.mkdir(exist_ok=True, parents=True)
    srcdata = _load_src_data()
    lookups = list(csv.DictReader(LOOKUPS_PATH.open()))

    with open(DEST_PATH, 'w') as dest:
        outs = csv.DictWriter(dest, fieldnames=HEADERS)
        outs.writeheader()

        for s in lookups:
            _x = extract_timeseries_by_state(s['postal_code'], s['full_name'], srcdata)
            _series = agg_state_series(sum_timeseries(_x))
            outs.writerows(_series)

    stderr.write(f"Wrote {DEST_PATH.stat().st_size} chars to {DEST_PATH}\n")


if __name__ == '__main__':
    main()
