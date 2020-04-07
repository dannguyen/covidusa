#!/usr/bin/env python
"""
This wrangling is really only run once, or anytime we update the census data, which is basically
never for the scope of this project
"""

from sys import path as syspath; syspath.append('./backend/scripts')
from utils.census import (derive_fips, derive_geolevel,
                            _typecast_field, WRANGLED_PATH as DEST_PATH)

from utils.utils import loggy

import csv
from pathlib import Path
import re


SRC_PATH = Path('./backend/data/fused/census-acs5-2018.csv')

BELOW_50K_KEYS = (
    'household_income_lt_10000_pct',
    'household_income_10000_to_14999_pct',
    'household_income_15000_to_24999_pct',
    'household_income_25000_to_34999_pct',
    'household_income_35000_to_49999_pct',
)

NULL_VALUES = ('-', '**', '(X)')


def derive_name(name, geolevel):
    if geolevel == 'county':
           return re.search(r', ([A-Za-z ]+)$', name).groups()[0]
    else:
        return name


def load_data():
    outdata = []
    with open(SRC_PATH) as src:
        for row in csv.DictReader(src):
            d = {}
            for k, v in row.items():
                if any(n == v for n in NULL_VALUES):
                    d[k] = None
                else:
                    d[k] = _typecast_field(k, v)
            outdata.append(d)
    return outdata


def wrangle_data(data):
    return [wrangle_row(row) for row in data]

def wrangle_row(row):
    """derive some calculations"""
    d = {}
    gid = d['census_geo_id'] = row['census_geo_id']
    geolev = derive_geolevel(gid)
    geofips = derive_fips(gid, geolev)
    # derive geo identifier fields
    d['name'] = derive_name(row.pop('census_geo_name'), geolev)
    d['geolevel'] = geolev
    d.update(geofips)
    d.update(row)

    # derive new calculations
    d['nonwhite_pct'] = 100 - row['white_pct'] if row['white_pct'] else None
    d['household_income_below_50k_pct'] = sum(row[h] for h in BELOW_50K_KEYS if row[h])

    return d


def main():
    outdata = wrangle_data(load_data())

    DEST_PATH.parent.mkdir(exist_ok=True, parents=True)
    with open(DEST_PATH, 'w') as dest:
        outs = csv.DictWriter(dest, fieldnames=outdata[0].keys())
        outs.writeheader()
        outs.writerows(outdata)
        loggy(f"Wrangled {len(outdata)} rows: {DEST_PATH}", __file__)

if __name__ == '__main__':
    main()
