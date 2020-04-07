#!/usr/bin/env python

import csv
from pathlib import Path
import re
from sys import stderr

FIPS_PATH = Path('backend/data/archives/lookups/fips.csv')
DEST_PATH = Path('backend/data/fused/nytimes-us.csv')
SRC_DIR = Path('backend/data/collected/nytimes')


SRC_SLUGS = ('us-counties', 'us-states')
OUT_HEADERS = ('id', 'state_abbr', 'geolevel', 'date', 'state', 'county','fips','confirmed','deaths')



def derive_geolevel(row):
    fips = row['fips']
    if len(fips) == 2 and re.match(r'[A-Z]{2}\b', row['id']):
        geo = 'state'
    elif re.match(r'\d{5}', fips):
        geo = 'county'
    elif not fips:
        if row['county'] == 'Unknown':
            geo = 'substate-unknown'
        else:
            geo = 'substate'
    else:
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



def load_fipsmap():
    with FIPS_PATH.open() as i:
        return list(csv.DictReader(i))



def main():
    fipsmap = load_fipsmap()
    outdata = []
    for slug in SRC_SLUGS:
        data = load_data(slug)
        fdata = fuse_data(data, fipsmap)
        stderr.write(f"{slug}: loaded {len(fdata)} rows\n")
        outdata.extend(fdata)

    outdata.sort(key=lambda d: (d['id'], d['date']))

    with open(DEST_PATH, 'w') as dest:
        outs = csv.DictWriter(dest, fieldnames=OUT_HEADERS)
        outs.writeheader()
        outs.writerows(outdata)
        stderr.write(f"Fused {len(outdata)} rows: {DEST_PATH}\n")




if __name__ == '__main__':
    main()
