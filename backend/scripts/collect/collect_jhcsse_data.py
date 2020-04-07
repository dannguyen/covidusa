#!/usr/bin/env python
from sys import path as syspath; syspath.append('./backend/scripts')
from utils.utils import loggy, fetch_and_save

from pathlib import Path

DEST_DIR = Path('backend/data/collected/jhcsse')
SRC_URLS = {
    'timeseries_confirmed': 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
    'timeseries_deaths': 'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv',
}


def main():
    print("DEPCRECATED AS OF 2020-03-27 for other datasets")
#    print("Yo, wait till JH has USA data separated: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data")

    pass
    DEST_DIR.mkdir(exist_ok=True, parents=True)
    for key, url in SRC_URLS.items():
        resp = requests.get(url)
        if resp.status_code == 200:
            stderr.write(f"{key}: Downloaded {len(resp.content)} bytes\n")
            dest_name = DEST_DIR.joinpath(f'{key}.csv')
            with open(dest_name, 'wb') as outs:
                stderr.write(f"\tWrote {len(resp.content)} bytes to: {dest_name}\n\n")
                outs.write(resp.content)
        else:
            raise ValueError(f"Unexpected status code: {resp.status_code} for url {url}")


if __name__ == '__main__':
    main()
