#!/usr/bin/env python

import csv
from collections import defaultdict
from datetime import date, timedelta
import json
from pathlib import Path
import re
from sys import stderr

FIPS_PATH = Path('backend/data/lookups/fips.csv')
SRC_PATH = Path('backend/data/wrangled/us-series.csv')
DEST_PATH = Path('backend/data/wrapped/summary.json')

SERIES_META = ('id', 'abbr', 'fips', 'geolevel', 'state_name', 'county_name', 'state_abbr')


def _daysdiff(dy, dx):
    if dx:
        return (date.fromisoformat(dy) - date.fromisoformat(dx)).days
    else:
        return None

def load_fipsmap():
    with FIPS_PATH.open() as i:
        return list(csv.DictReader(i))

def load_us_data():
    data = []
    with open(SRC_PATH) as src:
        for d in csv.DictReader(src):
            if d['geolevel'] == 'state':
                for key in d.keys():
                    if any(_h in key for _h in ('confirmed', 'deaths')):
                        if d[key]:
                            d[key] = float(d[key]) if 'pct' in key else int(d[key])

                data.append(d)
    return sorted(data, key=lambda d: d['date'])

                #     d['confirmed'] = int(d['confirmed']) if d['confirmed'] else 0
                #     d['deaths'] = int(d['deaths']) if d['deaths'] else 0
                # except Exception as e:
                #     import pdb; pdb.set_trace()
                #     raise e
                # else:




def summarize_overall(data):
    """data is assumed to be sorted by date"""
    meta = {}
#    data = sorted(data, key=lambda d: d['date'])
    meta['date_range'] = [
        data[0]['date'],
        data[-1]['date']
    ]
    dty = meta['date_range'][1]

    meta['latest'] = {
        'date': dty,
        'confirmed': sum(d['confirmed'] for d in data if d['date'] == dty),
        'deaths': sum(d['deaths'] for d in data if d['date'] == dty)

    }

    return meta

def summarize_state(abbr, alldata):
    """alldata is assumed to be sorted by date"""

    out = {}
    sdata = [row for row in alldata if row['id'] == abbr] # in wrangled data, state id IS postal code
    # try:

    # except Exception as err:
    #     import pdb; pdb.set_trace()
    #     raise err
    # else:
    latest = sdata[-1]
    out['id'] = out['abbr'] = latest['id']
    out['name'] = latest['state_name'] # rename state_name to name
    out['fips'] = latest['fips']
    # calculate milestones
    out['firsts'] = {}
    fd = next(s['date'] for s in sdata if s['confirmed'] > 0)
    out['firsts']['confirmed'] = {
        'date': fd, 'days_ago': _daysdiff(latest['date'], fd)
    }
    fd = next((s['date'] for s in sdata if s['deaths'] > 0), None)
    out['firsts']['death'] = {
        'date': fd, 'days_ago': _daysdiff(latest['date'], fd)
    }
    # get latest day numbers
    out['latest'] = {h: latest[h] for h in latest.keys() if h not in SERIES_META}


    return out


def main():
    DEST_PATH.parent.mkdir(exist_ok=True, parents=True)
    fipsmap = load_fipsmap()
    srcdata = load_us_data()

    outdata = {}
    outdata['overall'] = summarize_overall(srcdata)
    outdata['states'] = []

    for fd in fipsmap:
        abbr = fd['postal_code']
        outdata['states'].append(summarize_state(abbr, srcdata))




    outtext = json.dumps(outdata, indent=2)
    DEST_PATH.write_text(outtext)
    stderr.write(f"Wrangled: {len(outtext)} chars to {DEST_PATH}\n")


if __name__ == '__main__':
    main()
