#!/usr/bin/env python

"""
https://github.com/nytimes/covid-19-data
https://www.nytimes.com/article/coronavirus-county-data-us.html


https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html
"""

from pathlib import Path
import requests
from sys import stderr

DEST_DIR = Path('backend/data/collected/nytimes')
SRC_URLS = {
    'us-counties': 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv',
    'us-states': 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv',
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

