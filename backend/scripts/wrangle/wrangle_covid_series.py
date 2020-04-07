#!/usr/bin/env python
from sys import path as syspath; syspath.append('./backend/scripts')
from utils.census import load_wrangled_census
from utils.covid import WRANGLED_PATH as DEST_PATH
from utils.utils import days_between, loggy
from utils.settings import US_NATION_VALUES

import csv
from collections import defaultdict
import json
from pathlib import Path
import re

SRC_PATH = Path('backend/data/fused/nytimes-us.csv')


# should bring in utils.covid DAILY_STAT_FIELDS?
HEADERS = ('id', 'date', 'confirmed', 'deaths',
        'geolevel', 'state_abbr', 'fips', 'state_name', 'county_name',
        'confirmed_per_100k',
        'confirmed_daily_diff', 'confirmed_daily_diff_pct', 'deaths_daily_diff', 'deaths_daily_diff_pct',
        'confirmed_weekly_diff', 'confirmed_weekly_diff_pct', 'deaths_weekly_diff', 'deaths_weekly_diff_pct',
            )


def load_fused_series():
    # for now, this function assumes just U.S. things, i.e. things with FIPS
    data = []
    with open(SRC_PATH) as src:
        for row in csv.DictReader(src):
            row['state_name'] = row['state']
            row['county_name'] = row['county']
            # convert to numbers
            row['confirmed'] = int(row['confirmed'])
            row['deaths'] = int(row['deaths'])
            # deriviations

            data.append(row)
    return data


def fill_series(series):
    """unfortunately, the county-level reports aren't guaranteed to be contiguous, so fill them in
        assumes series to be sorted by date, and to belong to a single id"""
    outseries = []
    for i, row in enumerate(series):
        outseries.append(row.copy())
        if i < len(series) - 1:
            nrow = series[i+1]
            for dt in days_between(row['date'], nrow['date']):
                s = row.copy()
                s['date'] = dt
                outseries.append(s)

#     if len(series) != len(outseries):
#         print("fill check", series[0]['id'])
# #        import pdb; pdb.set_trace() # inject for fun
#         print("- series")
#         for d in series:
#             print(d['date'], d['confirmed'], d['deaths'])
#         print("- outseries")
#         for d in outseries:
#             print(d['date'], d['confirmed'], d['deaths'])

    return outseries

def wrangle_series(series, census):
    """this copies the series list and returns a new one, with new fields
    """
    outseries = []
    total_pop = census['total_population'] if census else None
    for i, row in enumerate(series):
        row['confirmed_per_100k'] = round(100000 * row['confirmed'] / total_pop) if total_pop else None


        if i < 1:
            pass
        else:
            q = series[i-1]
            qdate = q['date']
            row['confirmed_daily_diff'] = row['confirmed'] - q['confirmed']
            row['confirmed_daily_diff_pct'] = round(100.0 * row['confirmed_daily_diff'] / q['confirmed'], 1) if q['confirmed'] > 0 else None
            row['deaths_daily_diff'] = row['deaths'] - q['deaths']
            row['deaths_daily_diff_pct'] = round(100.0 * row['deaths_daily_diff'] / q['deaths'], 1) if q['deaths'] > 0 else None

        # after 7th row, data has a last week component
        if i < 7:
            pass
        else:
            q = series[i-7]
            qdate = q['date']
            row['confirmed_weekly_diff'] = row['confirmed'] - q['confirmed']
            row['confirmed_weekly_diff_pct'] = round(100.0 * row['confirmed_weekly_diff'] / q['confirmed'], 1) if q['confirmed'] > 0 else None
            row['deaths_weekly_diff'] = row['deaths'] - q['deaths']
            row['deaths_weekly_diff_pct'] = round(100.0 * row['deaths_weekly_diff'] / q['deaths'], 1) if q['deaths'] > 0 else None
        outseries.append(row)

    return outseries

def munge_nation_series(otherdata):
    """a special method that takes the wrangled states/county data, group sums it by day, and does
        a national total"""
    us_series = {}
    states_data = [o for o in otherdata if o['geolevel'] == 'state']
    for row in states_data:
        if row['state']:
            dt = row['date']
            if not us_series.get(dt):
                daydata = us_series[dt] = defaultdict(int)
                daydata['id'] = US_NATION_VALUES['id']
                daydata['geolevel'] = 'nation'
                daydata['fips'] = US_NATION_VALUES['fips']
                daydata['date'] = dt
                daydata['state_name'] = US_NATION_VALUES['name']
                daydata['state_abbr'] = daydata['county_name'] = None
            else:
                daydata = us_series[dt]

            daydata['day_state_count'] += 1
            for h in ('confirmed', 'deaths'):
                daydata[h] += row[h]


    outdata = sorted(us_series.values(), key=lambda x: x['date'])
    return outdata


def main():
    srcdata = load_fused_series()
    censusdata = load_wrangled_census()
    DEST_PATH.parent.mkdir(exist_ok=True, parents=True)
    xdata = []

    # get unique ids
    uids = set(d['id'] for d in srcdata)
    for uid in uids:
        series = sorted([d for d in srcdata if uid == d['id']], key=lambda d: d['date'])
        series = fill_series(series)

        ufips = series[0]['fips']
        census = next((c for c in censusdata if c['fips'] == ufips), None)

        series = wrangle_series(series, census)
        xdata.extend(series)


    xdata = sorted(xdata, key=lambda d: (d['id'], d['date']))

    ncensus = next((c for c in censusdata if c['geolevel'] == 'nation'), None)
    nation_data = wrangle_series(munge_nation_series(xdata), ncensus)

    with open(DEST_PATH, 'w') as dest:
        outs = csv.DictWriter(dest, fieldnames=HEADERS, extrasaction='ignore')
        outs.writeheader()
        outs.writerows(nation_data)
        outs.writerows(xdata)
        loggy(f"Wrote {len(nation_data) + len(xdata)} rows to {DEST_PATH}", __file__)


if __name__ == '__main__':
    main()
