#!/usr/bin/env python
"""
splits wrangled/timeseries into separate JSONs, with series and summaries
    e.g. data/wrapped/entities/NY.json
"""
import csv
import json
from pathlib import Path
from sys import stdout, stderr


DEST_DIR = Path('backend/data/wrapped/series/')
FIPS_PATH = Path('backend/data/lookups/fips.csv')
SRC_PATH= Path('backend/data/wrangled/timeseries.csv')


def load_fips():
    with FIPS_PATH.open() as i:
        return list(csv.DictReader(i))

def load_series():
    data = []
    with SRC_PATH.open() as ins:
        for row in csv.DictReader(ins):
            data.append(type_record(row))
    return data

def type_record(row):
    d = row.copy()
    for h in ('confirmed', 'confirmed_diff', 'deaths', 'deaths_diff'):
        d[h] = int(d[h])

    for h in ('confirmed_diff_pct', 'deaths_diff_pct'):
        try:
            d[h] = float(d[h]) if d[h] != '' else None
        except:
            import pdb; pdb.set_trace()
            raise

    return d

def main():
    DEST_DIR.mkdir(exist_ok=True, parents=True)
    fipsmap = load_fips()
    allseries = load_series()

    for f in fipsmap:
        fid = f['postal_code']
        fseries = []
        for row in allseries:
            if fid == row['id'] and row['confirmed'] > 0:
                d = row.copy()
                d.pop('id') # don't need this redundant key/val
                fseries.append(d)

        # let's sort in reverse-chrono order
        fseries = sorted(fseries, key=lambda x: x['date'], reverse=True)

        outdata = {'id': fid, 'name': f['full_name'], 'fips': f['fips'], 'series': fseries}

        destpath = DEST_DIR.joinpath(f'{fid}.json')
        stderr.write(f'{fid}: writing {len(fseries)} rows to: {destpath}\n')
        destpath.write_text(json.dumps(outdata, indent=2))

if __name__ == '__main__':
    main()



import pandas as pd
from pathlib import Path
SRC_PATH = Path('backend/data/wrangled/timeseries.csv')
df = pd.read_csv(SRC_PATH)
