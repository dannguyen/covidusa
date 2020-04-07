#!/usr/bin/env python
"""
splits wrangled/timeseries into separate JSONs, with series and summaries
    e.g. data/wrapped/entities/NY.json

For now, only loads **state totals**
"""
from sys import path as syspath; syspath.append('./backend/scripts')
from utils.covid import load_wrangled_covid
from utils.utils import loggy
from utils.settings import canonical_entity_ids


import csv
import json
from pathlib import Path

FIPS_PATH = Path('backend/data/archives/lookups/fips.csv')
DEST_DIR = Path('backend/data/wrapped/series/')

STATE_META_HEADERS = {'id', 'name', 'fips', 'state_abbr', 'geolevel'}
SERIES_META = ('id', 'abbr', 'fips', 'geolevel', 'state_name', 'county_name', 'state_abbr')



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
    wrangled_covid_data = load_wrangled_covid()

    _tots = {'fids': 0, 'records': 0, 'bytes': 0}
    for fid in canonical_entity_ids():
        fseries = [row for row in wrangled_covid_data if row['id'] == fid]
        fseries = sorted(fseries, key=lambda x: x['date'], reverse=False)
        _f0 = fseries[0]

        outdata = {'id': _f0['id'],
                    'name': _f0['state_name'],
                    'fips': _f0['fips'],
                    'abbr': _f0['state_abbr'],
                    'geolevel': _f0['geolevel']}
        # let's NOT sort in reverse-chrono order
        outdata['series'] = fseries
        jsontext = json.dumps(outdata, indent=2)

        destpath = DEST_DIR.joinpath(f'{fid}.json')
        destpath.write_text(jsontext)

        _tots['fids'] += 1
        _tots['records'] += len(fseries)
        _tots['bytes'] += len(jsontext)

    loggy(f"For {_tots['fids']} files in {DEST_DIR}", __file__)
    loggy(f"\twrote {_tots['records']} records and {_tots['bytes']} bytes")

if __name__ == '__main__':
    main()

