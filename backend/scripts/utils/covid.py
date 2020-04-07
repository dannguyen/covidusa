import csv
from pathlib import Path
from utils.settings import DEFAULT_GEOLEVELS

WRANGLED_PATH = Path('backend/data/wrangled/us-series.csv')

DAILY_STAT_FIELDS = ('confirmed',
                    'confirmed_per_100k',
                    'confirmed_daily_diff', 'confirmed_daily_diff_pct',
                     'deaths', 'deaths_daily_diff', 'deaths_daily_diff_pct')

SERIES_META_HEADERS = ('id', 'abbr', 'fips', 'geolevel', 'state_name', 'county_name', 'state_abbr')


def load_wrangled_covid(geolevels=DEFAULT_GEOLEVELS):
    data = []
    with open(WRANGLED_PATH) as src:
        for d in csv.DictReader(src):
            if d['geolevel'] == 'state' or d['geolevel'] == 'nation':
                for key in d.keys():
                    if any(_h in key for _h in ('confirmed', 'deaths')) and d[key]:
                        # d[key] = float(d[key]) if 'pct' in key else int(d[key])
                        d[key] = float(d[key]) if any(_k in key  for _k in ('_rate', '_pct')) else int(d[key])

                data.append(d)
    return sorted(data, key=lambda d: d['date'])



def strip_series_meta(record):
    d = {k: v for k, v in record.items() if k not in SERIES_META_HEADERS}
    return d
