#!/usr/bin/env python

"""
https://covidtracking.com/api/
states daily: https://covidtracking.com/api/states/daily.csv
us daily: https://covidtracking.com/api/us/daily.csv

Note: the NYT data will probably supercede this
"""

from pathlib import Path
import requests
from sys import stderr

DEST_DIR = Path('backend/data/collected/covidtracking')
SRC_URLS = {
    'states_daily': 'https://covidtracking.com/api/states/daily.csv',
    'us_daily': 'https://covidtracking.com/api/us/daily.csv',
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

