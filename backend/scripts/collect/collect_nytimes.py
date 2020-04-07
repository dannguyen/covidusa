#!/usr/bin/env python

"""
https://github.com/nytimes/covid-19-data
https://www.nytimes.com/article/coronavirus-county-data-us.html


https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html
"""
from sys import path as syspath; syspath.append('./backend/scripts')
from utils.utils import loggy, fetch_and_save

from pathlib import Path

DEST_DIR = Path('backend/data/collected/nytimes')
SRC_URLS = {
    'us-counties': 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv',
    'us-states': 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv',
}

def main():
    loggy("Collecting nytimes data", __file__)
    DEST_DIR.mkdir(exist_ok=True, parents=True)
    for slug, url in SRC_URLS.items():
        destpath = DEST_DIR.joinpath(f'{slug}.csv')
        fetch_and_save(url, destpath)


if __name__ == '__main__':
    main()

