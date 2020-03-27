#!/usr/bin/env python

import csv
from collections import defaultdict
import json
from pathlib import Path
import re
from sys import stderr

FIPS_PATH = Path('backend/data/lookups/fips.csv')
SRC_PATH = Path('backend/data/fused/nytimes-us.csv')
DEST_PATH = Path('backend/data/wrangled/us-series.csv')


HEADERS = ('id', 'date', 'confirmed', 'deaths',
        'confirmed_diff', 'confirmed_diff_pct', 'deaths_diff', 'deaths_diff_pct',
        'geolevel', 'state_abbr', 'fips', 'state_name', 'county_name',
            )

def derive_geolevel(row):
    fips = row['fips']
    if len(fips) == 2 and re.match(r'[A-Z]{2}\b', row['id']):
        geo = 'state'
    elif re.match(r'\d{5}', fips):
        geo = 'county'
    elif not fips:
        if row['county_name'] == 'Unknown':
            geo = 'substate-unknown'
        else:
            geo = 'metro'
    else:
        import pdb; pdb.set_trace(); raise
    return geo


def derive_id(row):
    # if row belongs to a state, then id is the postal_code/state_abbr
    fips = row.get('fips')
    if len(fips) == 2:
        # if row belongs to a county,then id is fips
        fid = row['state_abbr']
    elif re.match(r'\d{5}', fips):
        # if row has no fips, then concoct one
        fid = fips
    elif fips == "":
        fid = f'99999-{row["state_abbr"]}-{row["county"]}'
    else: # this shouldn't happen
        import pdb; pdb.set_trace(); raise
    return fid


def load_fipsmap():
    with FIPS_PATH.open() as i:
        return list(csv.DictReader(i))

def load_series():
    # for now, this function assumes just U.S. things, i.e. things with FIPS
    fipsmap = load_fipsmap()
    data = []
    with open(SRC_PATH) as src:
        for row in csv.DictReader(src):
            # the fused data doesn't have postal code/state_abbr, so we add them here
            try:
                if row['fips']:
                    row['state_abbr'] = next(x['postal_code'] for x in fipsmap if x['fips'] == row['fips'][0:2])
                else:
                    row['state_abbr'] = next(x['postal_code'] for x in fipsmap if x['full_name'] == row['state'])
            except:
                import pdb; pdb.set_trace(); raise

            row['state_name'] = row['state']
            row['county_name'] = row['county']
            # convert to numbers
            row['confirmed'] = int(row['confirmed'])
            row['deaths'] = int(row['deaths'])
            # deriviations

            row['id'] = derive_id(row)
            row['geolevel'] = derive_geolevel(row)
            data.append(row)
    return data


def wrangle_series(series):
    """this copies the series list and returns a new one, with new fields"""
    # get unique fips
    outdata = []
    for fid in set(d['fips'] for d in series):
        fdata = sorted([d for d in series if fid == d['fips']], key=lambda d: d['date'])
        for i, row in enumerate(fdata):
            if i < 1:
                row['confirmed_diff'] = row['deaths_diff'] = None
            else:
                q = fdata[i-1]
                row['confirmed_diff'] = row['confirmed'] - q['confirmed']
                row['confirmed_diff_pct'] = round(100.0 * row['confirmed_diff'] / q['confirmed'], 1) if q['confirmed'] > 0 else None
                row['deaths_diff'] = row['deaths'] - q['deaths']
                row['deaths_diff_pct'] = round(100.0 * row['deaths_diff'] / q['deaths'], 1) if q['deaths'] > 0 else None
            outdata.append(row)
    return outdata


def main():
    DEST_PATH.parent.mkdir(exist_ok=True, parents=True)
    srcdata = load_series()
    wdata = sorted(wrangle_series(srcdata), key=lambda d: (d['id'], d['date']))

    with open(DEST_PATH, 'w') as dest:
        outs = csv.DictWriter(dest, fieldnames=HEADERS, extrasaction='ignore')
        outs.writeheader()
        outs.writerows(wdata)
        stderr.write(f"Wrote {len(wdata)} rows to {DEST_PATH}\n")


if __name__ == '__main__':
    main()
