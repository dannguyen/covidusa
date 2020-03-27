#!/usr/bin/env python
"""
splits wrangled/timeseries into separate JSONs, with series and summaries
    e.g. data/wrapped/entities/NY.json

For now, only loads **state totals**
"""
import csv
import json
from pathlib import Path
from sys import stdout, stderr

FIPS_PATH = Path('backend/data/lookups/fips.csv')
SRC_PATH= Path('backend/data/wrangled/us-series.csv')

DEST_DIR = Path('backend/data/wrapped/series/')

STATE_META_HEADERS = {'id', 'name', 'fips', 'state_abbr', 'geolevel'}
SERIES_HEADERS = ('date', 'confirmed', 'deaths',
        'confirmed_diff', 'confirmed_diff_pct', 'deaths_diff', 'deaths_diff_pct',)


def load_fips():
    with FIPS_PATH.open() as i:
        return list(csv.DictReader(i))

def load_states_series():
    """returns a list of rows belonging to state-level calculations"""
    data = []
    with open(SRC_PATH) as src:
        for row in csv.DictReader(src):
            if row['geolevel'] == 'state':
                data.append(type_record(row))
    return data

def type_record(row):
    d = row.copy()
    for h in ('confirmed', 'confirmed_diff', 'deaths', 'deaths_diff'):
        d[h] = int(d[h]) if d.get(h) else None

    for h in ('confirmed_diff_pct', 'deaths_diff_pct'):
        try:
            d[h] = float(d[h]) if d.get(h) else None
        except:
            import pdb; pdb.set_trace(); raise


    return d

def main():
    DEST_DIR.mkdir(exist_ok=True, parents=True)
    fipsmap = load_fips()
    allseries = load_states_series()

    for f in fipsmap:
        abbr = f['postal_code']
        fseries = []
        for row in allseries:
            if abbr == row['id'] and row['confirmed'] > 0:
                d = {h: row[h] for h in SERIES_HEADERS}
                fseries.append(d)


        outdata = {'id': row['id'], 'name': row['state_name'], 'fips': f['fips'],
                    'abbr': row['state_abbr'], 'geolevel': row['geolevel']}
        # let's sort in reverse-chrono order
        outdata['series'] = sorted(fseries, key=lambda x: x['date'], reverse=True)

        destpath = DEST_DIR.joinpath(f'{abbr}.json')
        stderr.write(f'{abbr}: writing {len(fseries)} rows to: {destpath}\n')
        destpath.write_text(json.dumps(outdata, indent=2))

if __name__ == '__main__':
    main()

