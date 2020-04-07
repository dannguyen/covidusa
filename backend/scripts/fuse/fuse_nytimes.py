#!/usr/bin/env python
from sys import path as syspath; syspath.append('./backend/scripts')
from utils.fips import load_fipsmap
from utils.utils import loggy

import csv
from pathlib import Path
import re

DEST_PATH = Path('backend/data/fused/nytimes-us.csv')
SRC_DIR = Path('backend/data/collected/nytimes')


SRC_SLUGS = ('us-counties', 'us-states')
OUT_HEADERS = ('id', 'state_abbr', 'geolevel', 'date', 'state', 'county','fips','confirmed','deaths')



def derive_geolevel(row):
    fips = row['fips']
    if len(fips) == 2 and re.match(r'[A-Z]{2}\b', row['id']): # fips is '01' and row['id'] is 'AL'
        geo = 'state'
    elif re.match(r'\d{5}', fips): # fips is '01002'
        geo = 'county'
    elif not fips: # there is no fips
        if row['county'] == 'Unknown':
            geo = 'substate-unknown'
        else:
            geo = 'substate'
    else: # this shouldn't happen
        loggy("the 'row' contains values that do not make for a valid geolevel!")
        import pdb; pdb.set_trace(); raise
    return geo


def derive_id(row):
    """row is assumed to have state_abbr at this point"""
    fips = row.get('fips')
    if len(fips) == 2:
        # if row has fips length 2, then it is a state, and the id is state_abbr
        fid = row['state_abbr']
    elif re.match(r'\d{5}', fips):
        # if row belongs to a county, then id is fips
        fid = fips
    elif fips == "":
        # if no fips, then we make up an id
        fid = f'99999-{row["state_abbr"]}-{row["county"]}'
    else: # this shouldn't happen
        import pdb; pdb.set_trace(); raise
    return fid



def derive_abbr(row, fipsmap):
    # the fused data doesn't have postal code/state_abbr, so we add them here
    try:
        if row['fips']:
            abbr = next(x['postal_code'] for x in fipsmap if x['fips'] == row['fips'][0:2])
        else:
            abbr = next(x['postal_code'] for x in fipsmap if x['full_name'] == row['state'])
    except:
        import pdb; pdb.set_trace(); raise
    else:
        return abbr


def fuse_data(data, fipsmap):
    return [fuse_row(d, fipsmap) for d in data]


def fuse_row(row, fipsmap):
    row = row.copy()
    # rename 'cases' to 'confirmed'
    row['confirmed'] = row.pop('cases')
    row['state_abbr'] = derive_abbr(row, fipsmap)
    row['id'] = derive_id(row)
    row['geolevel'] = derive_geolevel(row)
    return row


def load_data(slug):
    outdata = []
    srcpath = Path(SRC_DIR.joinpath(f'{slug}.csv'))
    with open(srcpath) as src:
        for row in csv.DictReader(src):
            if not row.get('county'): # i.e. state-level data
                row['county'] = ''

            outdata.append(row)
    return outdata


def main():
    fipsmap = load_fipsmap()
    outdata = []
    for slug in SRC_SLUGS:
        data = load_data(slug)
        fdata = fuse_data(data, fipsmap)
        loggy(f"{slug}: loaded {len(fdata)} rows", __file__)
        outdata.extend(fdata)

    outdata.sort(key=lambda d: (d['id'], d['date']))

    with open(DEST_PATH, 'w') as dest:
        outs = csv.DictWriter(dest, fieldnames=OUT_HEADERS)
        outs.writeheader()
        outs.writerows(outdata)
        loggy(f"Fused {len(outdata)} rows: {DEST_PATH}", __file__)


if __name__ == '__main__':
    main()
