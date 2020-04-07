#!/usr/bin/env python
import csv
from pathlib import Path
import re
from sys import stderr


SRC_PATH = Path('./backend/data/fused/census-acs5-2018.csv')
DEST_PATH = Path('./backend/data/wrangled/census-acs5-2018.csv')

BELOW_50K_KEYS = (
    'household_income_lt_10000_pct',
    'household_income_10000_to_14999_pct',
    'household_income_15000_to_24999_pct',
    'household_income_25000_to_34999_pct',
    'household_income_35000_to_49999_pct',
)

NULL_VALUES = ('-', '**', '(X)')

CENSUS_GEOS = {
    'nation': '01',
    'division': '03',
    'state': '04',
    'county': '05',
    'place': '16'
}

def derive_geofips(gid):
    d = {}
    for geolev, num in CENSUS_GEOS.items():
        if num == gid[0:2]:
            # add fips
            d['geolevel'] = geolev
            if geolev == 'county':
                d['fips'] = gid[-5:]
                d['state_fips'] = d['fips'][0:2]
            elif geolev == 'state':
                d['state_fips'] = d['fips']  = gid[-2:]
            elif geolev == 'place':
                d['state_fips'] = re.search(r'US(\d{2})', gid).groups()[0]


                d['fips'] = None
            else:
                d['state_fips'] = d['fips'] = None
            return d


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
                elif '_pct' in k:
                    d[k] = float(v)
                else:
                    d[k] = v
            outdata.append(d)
    return outdata


def wrangle_data(data):
    return [wrangle_row(row) for row in data]

def wrangle_row(row):
    """derive some calculations"""
    d = {}
    gid = d['census_geo_id'] = row['census_geo_id']
    d.update(derive_geofips(gid))
    d['name'] = derive_name(row['census_geo_name'], d['geolevel'])

    d.update(row)
    d['nonwhite_pct'] = 100 - row['white_pct'] if row['white_pct'] else None
    d['household_income_below_50k_pct'] = sum(row[h] for h in BELOW_50K_KEYS if row[h])
    # remove unnecessary fields
    for h in ('census_geo_name', ):
        d.pop(h)

    return d



def main():
    outdata = wrangle_data(load_data())

    DEST_PATH.parent.mkdir(exist_ok=True, parents=True)
    with open(DEST_PATH, 'w') as dest:
        outs = csv.DictWriter(dest, fieldnames=outdata[0].keys())
        outs.writeheader()
        outs.writerows(outdata)
        stderr.write(f"Wrangled {len(outdata)} rows: {DEST_PATH}\n")

if __name__ == '__main__':
    main()
