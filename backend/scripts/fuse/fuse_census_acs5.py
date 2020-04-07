#!/usr/bin/env python
"""note that this script filters columns"""
from sys import path as syspath; syspath.append('./backend/scripts')
from utils.utils import loggy


from collections import defaultdict
import csv
from pathlib import Path
import re

SRC_DIR = Path('./backend/data/archives/census/originals/')
SRC_NAMES = {
    'dp05': 'ACSDP5Y2018.DP05/ACSDP5Y2018.DP05_data_with_overlays_2020-04-06T183545.csv',
    'dp03': 'ACSDP5Y2018.DP03/ACSDP5Y2018.DP03_data_with_overlays_2020-04-06T194908.csv',
}
DEST_PATH = Path('./backend/data/fused/census-acs5-2018.csv')


HEADERMAPS_DIR = Path('./backend/data/archives/census/lookups')


def load_original_data(slug):
    # returns dict of dicts, for which the census_geo_id is key
    outdata = {}
    headermap = list(csv.DictReader(HEADERMAPS_DIR.joinpath(f'headers-{slug}.csv').open()))
    srcpath = SRC_DIR.joinpath(SRC_NAMES[slug])
    with open(srcpath) as src:
        for i, row in enumerate(csv.DictReader(src)):
            if i > 0:
                d = {h['myname']: row[h['original']] for h in headermap}
                outdata[d['census_geo_id']] = d

    loggy(f"Read {len(outdata)} rows from: {srcpath}", __file__)
    return outdata

def fuse_data():
    """returns a list of dicts"""
    outdata = defaultdict(dict)
    for slug in SRC_NAMES.keys():
        data = load_original_data(slug)
        for key, val in data.items():
            try:
                outdata[key].update(val)
            except Exception as err:
                import pdb; pdb.set_trace(); raise err


    return sorted(outdata.values(), key=lambda x: x['census_geo_id'])

def main():
    outdata = fuse_data()

    DEST_PATH.parent.mkdir(exist_ok=True, parents=True)
    with open(DEST_PATH, 'w') as dest:
        outs = csv.DictWriter(dest, fieldnames=outdata[0].keys())
        outs.writeheader()
        outs.writerows(outdata)
        loggy(f"Fused {len(outdata)} rows: {DEST_PATH}", __file__)



if __name__ == '__main__':
    main()
