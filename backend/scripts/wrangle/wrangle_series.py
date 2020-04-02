#!/usr/bin/env python

import csv
from collections import defaultdict
from datetime import date, timedelta
import json
from pathlib import Path
import re
from sys import stderr

# FIPS_PATH = Path('backend/data/lookups/fips.csv')
SRC_PATH = Path('backend/data/fused/nytimes-us.csv')
DEST_PATH = Path('backend/data/wrangled/us-series.csv')


HEADERS = ('id', 'date', 'confirmed', 'deaths',
        'geolevel', 'state_abbr', 'fips', 'state_name', 'county_name',

        'confirmed_daily_diff', 'confirmed_daily_diff_pct', 'deaths_daily_diff', 'deaths_daily_diff_pct',
        'confirmed_weekly_diff', 'confirmed_weekly_diff_pct', 'deaths_weekly_diff', 'deaths_weekly_diff_pct',
            )


def _date_daysahead(dt, days):
    return (date.fromisoformat(dt) + timedelta(days=days)).isoformat()


def _daysdiff(dy, dx):
    return (date.fromisoformat(dy) - date.fromisoformat(dx)).days


def _days_between(dx, dy):
    diff = _daysdiff(dy, dx)
    if diff < 2:
        return [] # no days between consecutive days
    else:
        return [_date_daysahead(dx, i) for i in range(1, diff)]




# def load_fipsmap():
#     with FIPS_PATH.open() as i:
#         return list(csv.DictReader(i))

def loaddata():
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
            for dt in _days_between(row['date'], nrow['date']):
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

def wrangle_series(series):
    """this copies the series list and returns a new one, with new fields
    """
    outseries = []
    for i, row in enumerate(series):
        # the very first row represents the first day of confirmations, ostensibly, and no diffs can be calculated
        if i < 1:
            pass
        else:
            q = series[i-1]
            qdate = q['date']
            # # sanity check: make sure every subsequent row is 1 day after the previous one
            # if qdate != _date_daysago(row['date'], 1):
            #     #import pdb; pdb.set_trace() # inject for fun
            #     print(f"for id {uid}, row {i}: expected {row['date']} to be the next day after {qdate}")
            # end sanity check
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
            # # sanity check: make sure every subsequent row is 1 day after the previous one
            # if qdate != _date_daysago(row['date'], 7):
            #     #import pdb; pdb.set_trace() # inject for fun
            #     print(f"for id {uid}, row {i}: expected {row['date']} to be the next week after {qdate}")
            # end sanity check
            row['confirmed_weekly_diff'] = row['confirmed'] - q['confirmed']
            row['confirmed_weekly_diff_pct'] = round(100.0 * row['confirmed_weekly_diff'] / q['confirmed'], 1) if q['confirmed'] > 0 else None
            row['deaths_weekly_diff'] = row['deaths'] - q['deaths']
            row['deaths_weekly_diff_pct'] = round(100.0 * row['deaths_weekly_diff'] / q['deaths'], 1) if q['deaths'] > 0 else None
        outseries.append(row)

    return outseries


def main():
    DEST_PATH.parent.mkdir(exist_ok=True, parents=True)
    outdata = []
    srcdata = loaddata()
    # get unique ids
    uids = set(d['id'] for d in srcdata)
    for uid in uids:
        series = sorted([d for d in srcdata if uid == d['id']], key=lambda d: d['date'])
        series = fill_series(series)
        series = wrangle_series(series)
        outdata.extend(series)


    outdata = sorted(outdata, key=lambda d: (d['id'], d['date']))

    with open(DEST_PATH, 'w') as dest:
        outs = csv.DictWriter(dest, fieldnames=HEADERS, extrasaction='ignore')
        outs.writeheader()
        outs.writerows(outdata)
        stderr.write(f"Wrote {len(outdata)} rows to {DEST_PATH}\n")


if __name__ == '__main__':
    main()
