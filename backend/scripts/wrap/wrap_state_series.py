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

FIPS_PATH = Path('backend/data/archives/lookups/fips.csv')
SRC_PATH= Path('backend/data/wrangled/us-series.csv')

DEST_DIR = Path('backend/data/wrapped/series/')

STATE_META_HEADERS = {'id', 'name', 'fips', 'state_abbr', 'geolevel'}
SERIES_META = ('id', 'abbr', 'fips', 'geolevel', 'state_name', 'county_name', 'state_abbr')



def load_fips():
    with FIPS_PATH.open() as i:
        return list(csv.DictReader(i))



def load_us_data():
    data = []
    with open(SRC_PATH) as src:
        for d in csv.DictReader(src):
            if d['geolevel'] == 'state':
                for key in d.keys():
                    if any(_h in key for _h in ('confirmed', 'deaths')):
                        if d[key]:
                            d[key] = float(d[key]) if any(_k in key  for _k in ('_rate', '_pct')) else int(d[key])

                data.append(d)
    return sorted(data, key=lambda d: d['date'])



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
    allseries = load_us_data()

    for f in fipsmap:
        abbr = f['postal_code']
        fseries = [row for row in allseries if row['id'] == abbr]
        fx = fseries[0]
        # for row in allseries:
        #     if abbr == row['id'] and row['confirmed'] > 0:
        #         d = {h: row[h] for h in SERIES_HEADERS}
        #         fseries.append(d)


        outdata = {'id': fx['id'], 'name': fx['state_name'], 'fips': fx['fips'],
                    'abbr': fx['state_abbr'], 'geolevel': fx['geolevel']}
        # let's NOT sort in reverse-chrono order
        outdata['series'] = sorted(fseries, key=lambda x: x['date'], reverse=False)

        destpath = DEST_DIR.joinpath(f'{abbr}.json')
        stderr.write(f'{abbr}: writing {len(fseries)} rows to: {destpath}\n')
        destpath.write_text(json.dumps(outdata, indent=2))

if __name__ == '__main__':
    main()

