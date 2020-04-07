from utils.fips import load_fipsmap

DEFAULT_GEOLEVELS = ('state', 'nation')

US_NATION_VALUES = {
    'fips': 'USA',
    'name': 'United States',
    'id': 'USA',
}


def canonical_entity_ids():
    """
    for now: just the USA, states, and territories
    """
    return ['USA'] + canonical_state_ids()


def canonical_state_ids():
    return [f['postal_code'] for f in load_fipsmap()]
