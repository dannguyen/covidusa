from utils.settings import DEFAULT_GEOLEVELS, US_NATION_VALUES
import csv
from pathlib import Path
import re


WRANGLED_PATH = Path('backend/data/wrangled/census.csv')

CENSUS_GEOCODES = {
    'nation': '01',
    'division': '03',
    'state': '04',
    'county': '05',
    'place': '16'
}


def derive_fips(gid, geolevel):
    d = {}
    if geolevel == 'nation':
        d['fips'] = US_NATION_VALUES['fips']
        d['state_fips'] = None

    elif geolevel == 'county':
        d['fips'] = gid[-5:]
        d['state_fips'] = d['fips'][0:2]
    elif geolevel == 'state':
        d['state_fips'] = d['fips']  = gid[-2:]
    elif geolevel == 'place':
        d['state_fips'] = re.search(r'US(\d{2})', gid).groups()[0]
        d['fips'] = None
    else:
        d['state_fips'] = d['fips'] = None
    return d

def derive_geolevel(gid):
    code = gid[0:2]
    geolevel = next((my_geolabel for my_geolabel, censuscode in CENSUS_GEOCODES.items() if censuscode == code), None)
    if geolevel:
        return geolevel
    else:
        raise ValueError(f"the census geo id of '{gid}' does not belong to a valid geolevel: {CENSUS_GEOCODES}")



def get_nation_census(censusdata):
    return next((c for c in censusdata if c['geolevel'] == 'nation'))

def get_state_census(censusdata, fips):
    return next((row for row in censusdata if row['fips'] == fips), {})

def load_wrangled_census(geolevels=DEFAULT_GEOLEVELS):
    """ just the states"""
    data = []
    with open(WRANGLED_PATH) as src:
        for d in csv.DictReader(src):
            if d['geolevel'] in geolevels:
                for key, val in d.items():
                    d[key] = _typecast_field(key, val)
                data.append(d)
    return data

def _typecast_field(fieldname, val):
    if val and any(h in fieldname for h in ('_pct', '_ratio', 'total_', '_total', '_median', '_total',)):
        if any(k in fieldname for k in ('_pct', '_ratio')):
            return float(val)
        else:
            return int(val)
    else:
        return val


