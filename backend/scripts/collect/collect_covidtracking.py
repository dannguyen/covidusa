#!/usr/bin/env python

"""
https://covidtracking.com/api/
states daily: https://covidtracking.com/api/states/daily.csv
us daily: https://covidtracking.com/api/us/daily.csv

Note: the NYT data will probably supercede this
"""
from sys import path as syspath; syspath.append('./backend/scripts')
from utils.utils import loggy, fetch_and_save

from pathlib import Path

DEST_DIR = Path('backend/data/collected/covidtracking')
SRC_URLS = {
    'states-daily': 'https://covidtracking.com/api/states/daily.csv',
    'us-daily': 'https://covidtracking.com/api/us/daily.csv',
}

def main():
    loggy("Collecting covidtracking data", __file__)
    DEST_DIR.mkdir(exist_ok=True, parents=True)
    for slug, url in SRC_URLS.items():
        destpath = DEST_DIR.joinpath(f'{slug}.csv')
        fetch_and_save(url, destpath)


if __name__ == '__main__':
    main()

