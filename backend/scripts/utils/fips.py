import csv
from pathlib import Path

FIPS_PATH = Path('backend/data/archives/lookups/fips.csv')


def load_fipsmap():
    with FIPS_PATH.open() as i:
        return list(csv.DictReader(i))
