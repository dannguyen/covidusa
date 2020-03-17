#!/usr/bin/env python

import csv
from pathlib import Path
import re
from sys import stderr

DEST_PATH = Path('data/fused/jhcsse_normalized.csv')
SRC_DIR = Path('data/collected/jhcsse/')
SRC_FILES = {
    'confirmed': SRC_DIR.joinpath('timeseries_confirmed.csv'),
    'deaths': SRC_DIR.joinpath('timeseries_deaths.csv')
}

COMMON_HEADERS = ('country_region', 'province_state', 'latitude', 'longitude')


def load_timeseries_data():
    """returns a dict of lists of dicts, e.g. {'confirmed': [{'country_region': 'US'...}], 'deaths': [{...}]}"""
    outdata = {}
    for srckey, srcpath in SRC_FILES.items():
        outrows = []
        for inrow in csv.DictReader(srcpath.open()):
            o = {}
            for header, value in inrow.items():
                if header == 'Province/State':
                    o['province_state'] = value
                elif header == 'Country/Region':
                    o['country_region'] = value
                elif header == 'Lat':
                    o['latitude'] = value
                elif header == 'Long':
                    o['longitude'] = value
                else: # it's a date header, e.g. 2/7/20
                    try:
                        _m, _d, _y = header.split('/')
                    except Exception as err:
                        stderr.write(f"Unexpected header: {header}\n")
                        raise err
                    else:
                        dt = f"20{_y}-{_m.rjust(2, '0')}-{_d.rjust(2, '0')}"
                        o[dt] = value

            outrows.append(o)
        outdata[srckey] = sorted(outrows, key=lambda r: [r[h] for h in COMMON_HEADERS])

    return outdata

def normalize_timeseries_data(indata):
    # produces a single list of dicts
    #
    # `indata` is expected to be a *validated* dict of lists of dicts, with the lists having the same
    #   headers and number of rows
    normaldata = []

    xdata = list(indata.values())[0]
    xheaders = list(xdata[0].keys())

    # date_headers = [xk for xk in xheaders if xk not in COMMON_HEADERS] #
    date_headers = sorted([h for h in xheaders if re.match(r'\d{4}-\d{2}-\d{2}', h)])

    # in the normalized data, each place/date combination has its own record
    for dateval in date_headers:
        for xrow in xdata:
            nrow = {}
            nrow['date'] = dateval
            # populate common headers
            for h in COMMON_HEADERS:
                nrow[h] = xrow[h]
            # for each dataset in indata, extract the corresponding datevalue
            for dkey, dataset in indata.items():
                drow = next(d for d in dataset if all(d[h] == nrow[h] for h in COMMON_HEADERS))

                nrow[dkey] = drow[dateval]

            normaldata.append(nrow)
    return normaldata

        # populate


def validate_timeseries_data(indata):
    # make sure that the `timeseries_confirmed` and `timeseries_deaths` has exactly
    # the same country/region names, province/state names, and dates
    #
    # `indata` is expected to be a dict of lists of dicts, with the lists
    #    sorted in alphabetical order across the common fields

    xrows = list(indata.values())[0]
    xkeys = xrows[0].keys()

    # make sure common headers is in the first dataset
    for h in COMMON_HEADERS:
        if not h in xkeys:
            raise ValueError(f"Did not find common header `{h}` in first dataset `{list(indata.keys())[0]}`")

    # make sure uncommon headers are in expected date format
    _dateheaders = [xk for xk in xkeys if xk not in COMMON_HEADERS]
    for k in _dateheaders:
        if not re.match(r'\d{4}-\d{2}-\d{2}', k):
            raise ValueError(f"Unexpected date header `{k}` in first dataset `{list(indata.keys())[0]}`")


    for dname, data in indata.items():
        stderr.write(f"Validating dataset {dname}:\n")

        dkeys = data[0].keys()

        # make sure each dataset has the same number of columns
        if not len(xkeys) == len(dkeys):
            raise ValueError(f"Dataset `{dname}` has {len(dkeys)} columns; expected {len(xkeys)} columns")
        else:
            stderr.write(f"- Dataset `{dname}` has {len(xkeys)} columns.\n")

        # make sure each dataset has the same number of rows

        if not len(xrows) == len(data):
            raise ValueError(f"Dataset `{dname}` has {len(data)} rows; expected {len(xrows)} rows")
        else:
            stderr.write(f"- Dataset `{dname}` has {len(xrows)} rows.\n")

        # make sure each dataset has the same column names
        if not xkeys == dkeys:
            raise ValueError(f"Dataset `{dname}` lacks these columns: {set(xkeys) - set(dkeys)} and " +
                                f"has these erroneous columns: {set(dkeys) - set(xkeys)}")

        # make sure each dataset has the same values for common headers
        for i, d in enumerate(data):
            x = xrows[i]
            for h in COMMON_HEADERS:
                if not d[h] == x[h]:
                    raise ValueError(f"For cell {dname}[{i}][{h}]; expected `{x[h]}` but got `{d[h]}`")




def main():
    tdata = load_timeseries_data()
    validate_timeseries_data(tdata)
    ndata = normalize_timeseries_data(tdata)

    outheaders = ndata[0].keys()
    stderr.write(f"Normalized data has dimensions {len(outheaders)}x{len(ndata)}\n")

    # get unique dates
    udates = list(set(n['date'] for n in ndata))
    stderr.write(f"{len(udates)} days, from {min(udates)} to {max(udates)}\n")

    DEST_PATH.parent.mkdir(exist_ok=True, parents=True)
    with open(DEST_PATH, 'w') as dest:
        outs = csv.DictWriter(dest, fieldnames=outheaders)
        outs.writeheader()
        outs.writerows(ndata)
        stderr.write(f"Wrote {len(ndata)} rows to: {DEST_PATH}\n")



if __name__ == '__main__':
    main()
