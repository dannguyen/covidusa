#!/usr/bin/env python

"""
This script produces two kinds of wrapped output:

    outputs into wrapped/summary.json
    outputs into wrapped/entities/

"""


from sys import path as syspath; syspath.append('./backend/scripts')
from utils.census import load_wrangled_census, get_entity_census_by_fips
from utils.covid import load_wrangled_covid, strip_series_meta, DAILY_STAT_FIELDS
from utils.fips import load_fipsmap
from utils.utils import daysdiff, date_daysahead, loggy
from utils.settings import canonical_state_ids, US_NATION_VALUES


import json
from pathlib import Path



SUMMARY_DEST_PATH = Path('backend/data/wrapped/summary.json')
ENTITY_DEST_DIR = Path('backend/data/wrapped/entities/')


def _agg_firsts(series, latest_date):
    out = {}
    fdate = next(s['date'] for s in series if s['confirmed'] > 0)
    out['confirmed'] = {
        'date': fdate, 'days_ago': daysdiff(latest_date, fdate)
    }

    fdate = next((s['date'] for s in series if s['confirmed'] > 100), None)
    out['confirmed_100'] = {
        'date': fdate, 'days_ago': daysdiff(latest_date, fdate)
    } if fdate else {}


    fdate = next((s['date'] for s in series if s['deaths'] > 0), None)
    out['death'] = {
        'date': fdate, 'days_ago': daysdiff(latest_date, fdate)
    } if fdate else {}

    return out

def _agg_last_14_days(series, latest_date):
    out = {}
    maxdays = min(14, len(series) - 1)

    out['dates'] = [date_daysahead(latest_date, -i) for i in range(1, maxdays)]

    for h in DAILY_STAT_FIELDS:
        out[h] = []
        for i in range(1, maxdays):
            j = -(i+1)
            out[h].append(series[j][h])

    return out
        # for i in range(1, 14):
            # if i+1 > len(sdata):
            #     break
            # else:
            #     j = 0 - (i+1)
            #     dlast[h].append(sdata[j][h])


def get_entity_series(eid, wrangled_data):
    """
        eid is our unique entity ids, i.e. "CA" "IL" etc, basically, state abbrevs for now, before we
        include international entities.

        'USA' is also allowed

    """
#   series = [strip_series_meta(row) for row in wrangled_data if row['id'] == eid]
    series = [row for row in wrangled_data if row['id'] == eid]
    series = sorted(series, key=lambda x: x['date'], reverse=False)
    return series


def get_entity_historical_records(eid, wrangled_data):
    out = [strip_series_meta(s) for s in get_entity_series(eid, wrangled_data)]
    return out


def summarize_entity(series, census):
    """
    IMPORTANT: for now, series/census is expected to belong to a U.S. state or 'USA', in the case of a nation

    DEPRECATED eid(str): is our unique entity ids, i.e. "USA" or "CA" "IL" etc, (basically, state abbrevs for now)

    series(list): the list of dicts belonging to that eid, e.g. called from get_entity_series()

    census(dict): the row belonging to the eid, i.e. called from get_entity_census_by_fips(eid)

    Returns: (dict)
    """

    out = {}

    # get top-level meta attributes
    latest = series[-1]
    out['id'] = latest['id']

    try:
        out['census_geo_id'] = census['census_geo_id'] if census else None

        out['name'] = latest['state_name'] # rename state_name to name
    except Exception as err:
        import pdb; pdb.set_trace()
        raise err

    out['fips'] = latest['fips']
    out['geolevel'] = latest['geolevel']
    out['state_abbr'] = latest['state_abbr']

    # add latest entry
    out['latest'] = strip_series_meta(latest)
    # calculate milestones
    out['firsts'] = _agg_firsts(series, latest['date'])
    # last 14 days array
    out['last_14_days'] = _agg_last_14_days(series, latest['date'])

    out['census'] = census

    return out


def wrap_nation(all_wrangled, all_census):
    fips = US_NATION_VALUES['fips']
    series = get_entity_series(fips, all_wrangled)
    census = get_entity_census_by_fips(fips, all_census)
    return summarize_entity(series, census)

def wrap_states(all_wrangled, all_census):
    """by convention, all state entity ids are the same as their postal_code"""
    outs = []
    for f in load_fipsmap():
        eid = f['postal_code']
        fips = f['fips']
        series = get_entity_series(eid, all_wrangled)
        census = get_entity_census_by_fips(fips, all_census)
        d = summarize_entity(series, census)
        outs.append(d)
    return outs


def output_summary(nation, states):
    SUMMARY_DEST_PATH.parent.mkdir(exist_ok=True, parents=True)

    outdata = {}
    outdata['overall'] = {'status': '200'} # DTK summarize_covid_overall(covid_data)
    outdata['nation'] = nation
    outdata['states'] = states

    outtext = json.dumps(outdata, indent=2)
    SUMMARY_DEST_PATH.write_text(outtext)
    loggy(f"Wrangled: {len(outtext)} chars to {SUMMARY_DEST_PATH}", __file__ + ':summary')


def output_entity(eid, data):
    """a wrapped entity has the same data as a summarized entity,
        but also a "records" attribute that represents info on every day"""
    destpath = ENTITY_DEST_DIR.joinpath(f'{eid}.json')

    jsontext = json.dumps(data, indent=2)
    destpath.write_text(jsontext)
    return (destpath, jsontext)

def output_entities(entities, all_wrangled):
    ENTITY_DEST_DIR.mkdir(exist_ok=True, parents=True)

    totebytes = 0
    for e in entities:
        o = e.copy()
        o['records'] = get_entity_historical_records(o['id'], all_wrangled)

        # just some loggin
        dest, txt = output_entity(o['id'], o)
        totebytes += len(txt)

    loggy(f"{len(entities)} entities, {totebytes} chars written to: {ENTITY_DEST_DIR}", __file__ + ':entities')


def main():
    covid_data = load_wrangled_covid()
    census_data = load_wrangled_census()

    nation = wrap_nation(covid_data, census_data)
    states = wrap_states(covid_data, census_data)

    output_summary(nation=nation, states=states)
    output_entities([nation] + states, covid_data)


if __name__ == '__main__':
    main()
