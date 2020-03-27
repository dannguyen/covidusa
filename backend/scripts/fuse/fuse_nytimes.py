#!/usr/bin/env python

import csv
from pathlib import Path
import re
from sys import stderr

DEST_PATH = Path('backend/data/fused/nytimes-us.csv')
SRC_DIR = Path('backend/data/collected/nytimes')
SRC_SLUGS = ('us-counties', 'us-states')


OUT_HEADERS = ('date','state','county','fips','confirmed','deaths')


def load_data(slug):
    outdata = []
    srcpath = Path(SRC_DIR.joinpath(f'{slug}.csv'))
    with open(srcpath) as src:
        for row in csv.DictReader(src):
            if not row.get('county'): # i.e. state-level data
                row['county'] = ''
            row['confirmed'] = row.pop('cases')
            outdata.append(row)
    return outdata

def main():
    outdata = []
    for slug in SRC_SLUGS:
        sdata = load_data(slug)
        stderr.write(f"{slug}: loaded {len(sdata)} rows\n")
        outdata.extend(sdata)

    # sort by state, county, and chrono date
    outdata.sort(key=lambda d: (d['state'], d['county'], d['date']))

    with open(DEST_PATH, 'w') as dest:
        outs = csv.DictWriter(dest, fieldnames=OUT_HEADERS)
        outs.writeheader()
        outs.writerows(outdata)
        stderr.write(f"Fused {len(outdata)} rows: {DEST_PATH}\n")




if __name__ == '__main__':
    main()
