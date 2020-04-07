#!/usr/bin/env python
from sys import path as syspath; syspath.append('./backend/scripts')
from utils.census import load_wrangled_census, get_nation_census, get_state_census
from utils.covid import load_wrangled_covid, strip_series_meta, DAILY_STAT_FIELDS
from utils.utils import daysdiff, date_daysahead, loggy
from utils.settings import canonical_entity_ids


import csv
from collections import defaultdict
from datetime import date, timedelta
import json
from pathlib import Path
import re

DEST_PATH = Path('backend/data/wrapped/summary.json')
FIPS_PATH = Path('backend/data/archives/lookups/fips.csv')







def summarize_covid_overall(data):
    """data is assumed to be sorted by date"""
    meta = {}
#    data = sorted(data, key=lambda d: d['date'])
    meta['date_range'] = [
        data[0]['date'],
        data[-1]['date']
    ]
    dty = meta['date_range'][1]
    return meta

def summarize_covid_state(abbr, alldata):
    """alldata is assumed to be sorted by date"""

    out = {}
    sdata = [row for row in alldata if row['id'] == abbr] # in wrangled data, state id IS postal code
    # try:

    # except Exception as err:
    #     import pdb; pdb.set_trace()
    #     raise err
    # else:
    latest = sdata[-1]
    ldate = latest['date']
    out['id'] = out['abbr'] = latest['id']
    out['name'] = latest['state_name'] # rename state_name to name
    out['fips'] = latest['fips']
    # calculate milestones
    out['firsts'] = {}
    fd = next(s['date'] for s in sdata if s['confirmed'] > 0)
    out['firsts']['confirmed'] = {
        'date': fd, 'days_ago': daysdiff(latest['date'], fd)
    }

    fd = next((s['date'] for s in sdata if s['confirmed'] > 100), None)
    out['firsts']['confirmed_100'] = {
        'date': fd, 'days_ago': daysdiff(latest['date'], fd)
    } if fd else {}


    fd = next((s['date'] for s in sdata if s['deaths'] > 0), None)
    out['firsts']['death'] = {
        'date': fd, 'days_ago': daysdiff(latest['date'], fd)
    } if fd else {}

    # get latest day numbers
    out['latest'] = strip_series_meta(latest)


    # get last 14 days
    dlast = out['last_14_days'] = {}
    maxdays = min(14, len(sdata) - 1)

    dlast['dates'] = [date_daysahead(ldate, -i) for i in range(1, maxdays)]


    for h in DAILY_STAT_FIELDS:
        dlast[h] = []
        for i in range(1, 14):
            if i+1 > len(sdata):
                break
            else:
                j = 0 - (i+1)
                dlast[h].append(sdata[j][h])
    return out


def main():
    DEST_PATH.parent.mkdir(exist_ok=True, parents=True)
    covid_data = load_wrangled_covid()
    census_data = load_wrangled_census()

    outdata = {}
    outdata['overall'] = summarize_covid_overall(covid_data)
    outdata['nation'] = {}
    outdata['states'] = []


    for fid in canonical_entity_ids():
        d = summarize_covid_state(fid, covid_data)
        if fid == 'USA':
            outdata['nation'] = d
            d['census'] = get_nation_census(census_data)

        else:
            # territories do not have census info other than DC and PR
            d['census'] = get_state_census(census_data, fid)
            outdata['states'].append(d)


    outdata['states'].sort(key=lambda x: x['id'])


    outtext = json.dumps(outdata, indent=2)
    DEST_PATH.write_text(outtext)
    loggy(f"Wrangled: {len(outtext)} chars to {DEST_PATH}", __file__)


if __name__ == '__main__':
    main()
