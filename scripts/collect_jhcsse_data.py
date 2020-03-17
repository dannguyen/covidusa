#!/usr/bin/env python
from pathlib import Path
import requests
from sys import stderr

DEST_DIR = Path('data/collected/jhcsse')
SRC_URLS = {
    'timeseries_confirmed': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv',
    'timeseries_deaths': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv',
}


def main():
    DEST_DIR.mkdir(exist_ok=True, parents=True)
    for key, url in SRC_URLS.items():
        resp = requests.get(url)
        if resp.status_code == 200:
            stderr.write(f"{key}: Downloaded {len(resp.content)} bytes\n")
            dest_name = DEST_DIR.joinpath(f'{key}.csv')
            with open(dest_name, 'wb') as outs:
                stderr.write(f"\tWrote {len(resp.content)} bytes to: {dest_name}\n\n")
                outs.write(resp.content)


if __name__ == '__main__':
    main()
