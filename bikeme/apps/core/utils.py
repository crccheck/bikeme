from __future__ import division

import logging

from project_runpy import ColorizingStreamHandler
from dateutil.parser import parse
from dateutil.tz import gettz
import requests

from .models import Market, Station, Snapshot


logger = logging.getLogger(__name__)
logger.addHandler(ColorizingStreamHandler())


def setfield(obj, fieldname, value):
    """Fancy setattr with debugging."""
    old = getattr(obj, fieldname)
    if str(old) != str(value):
        setattr(obj, fieldname, value)
        if not hasattr(obj, '_is_dirty'):
            obj._is_dirty = []
            obj._dirty_fields = []
        obj._is_dirty.append("%s %s->%s" % (fieldname, old, value))
        obj._dirty_fields.append(fieldname)


def update_with_defaults(obj, data):
    """
    Fancy way to update `obj` with `data` dict.

    Returns True if data changed and  was saved.
    """
    for key, value in data.items():
        setfield(obj, key, value)
    if getattr(obj, '_is_dirty', None):
        logger.debug(obj._is_dirty)
        obj.save(update_fields=obj._dirty_fields)
        del obj._is_dirty
        del obj._dirty_fields
        return True


def update_market_bcycle(market):
    url_tmpl = 'http://bikeme-api.herokuapp.com/{market}/'
    response = requests.get(url_tmpl.format(market=market.slug))
    data = response.json()
    scraped_at = parse(data['now'])
    for row in data['results']:
        state, zip_code = row['state_zip'].split(' ', 2)
        capacity = row['bikes'] + row['docks']
        defaults = dict(
            latitude=row['latitude'],
            longitude=row['longitude'],
            street=row['street'],
            zip=zip_code,
            state=state,
            capacity=capacity,
            updated_at=scraped_at,
        )
        station, created = Station.objects.get_or_create(
            name=row['name'],
            market=market,
            defaults=defaults,
        )
        if not created:
            update_with_defaults(station, defaults)
        defaults = dict(
            bikes=row['bikes'],
            docks=row['docks'],
            status=row['status'],
        )
        snapshot, created = Snapshot.objects.get_or_create(
            timestamp=scraped_at,
            station=station,
            defaults=defaults,
        )
        station.latest_snapshot = snapshot
        station.save()
    qs = market.stations.filter(updated_at__lt=scraped_at)
    if qs.exists():
        logger.info('Marking as inactive')


def update_market_alta(market):
    # http://www.altabicycleshare.com/locations
    lookup = {
        'chattanooga': {
            'url': 'http://bikechattanooga.com/stations/json/',
            'timezone': 'America/New_York',
        },
        'chicago': {
            'url': 'http://divvybikes.com/stations/json/',
            'timezone': 'America/Chicago',
        },
        'nyc': {
            'url': 'http://citibikenyc.com/stations/json/',
            'timezone': 'America/New_York',
        },
    }
    status_lookup = {
        'In Service': 'available',
        'Not In Service': 'outofservice',
    }
    market_data = lookup[market.slug]
    response = requests.get(market_data['url'])
    data = response.json()
    tz = gettz(market_data['timezone'])
    scraped_at = parse(data['executionTime']).replace(tzinfo=tz)
    for row in data['stationBeanList']:
        defaults = dict(
            latitude=row['latitude'],
            longitude=row['longitude'],
            street=row['stAddress1'],
            zip=row['postalCode'],
            capacity=row['totalDocks'],
            updated_at=scraped_at,
        )
        station, created = Station.objects.get_or_create(
            name=row['stationName'],
            market=market,
            defaults=defaults,
        )
        if not created:
            update_with_defaults(station, defaults)
        defaults = dict(
            bikes=row['availableBikes'],
            docks=row['availableDocks'],
            status=status_lookup.get(row['statusValue'], 'outofservice'),
        )
        snapshot, created = Snapshot.objects.get_or_create(
            timestamp=scraped_at,
            station=station,
            defaults=defaults,
        )
        station.latest_snapshot = snapshot
        station.save()


def update_market_citi(market):
    """Based on citybik.es api."""
    response = requests.get('http://api.citybik.es/citi-bike-nyc.json')  # XXX
    data = response.json()
    for row in data:
        capacity = row['bikes'] + row['free']
        timestamp = row['timestamp'].rsplit('.', 2)[0] + 'Z'  # round down
        scraped_at = parse(timestamp)
        defaults = dict(
            latitude=row['lat'] / 1000000,
            longitude=row['lng'] / 1000000,
            capacity=capacity,
            updated_at=scraped_at,
        )
        station, created = Station.objects.get_or_create(
            name=row['name'],
            market=market,
            defaults=defaults,
        )
        if not created:
            update_with_defaults(station, defaults)
        defaults = dict(
            bikes=row['bikes'],
            docks=row['free'],
        )
        snapshot, created = Snapshot.objects.get_or_create(
            timestamp=scraped_at,
            station=station,
            defaults=defaults,
        )
        station.latest_snapshot = snapshot
        station.save()
    # WISHLIST auto mark stations as inactive


def update_all_markets(*market_slugs):
    if market_slugs:
        queryset = Market.objects.filter(slug__in=market_slugs)
    else:
        queryset = Market.objects.filter(active=True)
    for market in queryset:
        if market.type == 'bcycle':
            update_market_bcycle(market)
        elif market.type == 'alta' or market.slug == 'divvy' or market.slug == 'nyc':
            update_market_alta(market)
        else:
            logger.warn(u'Unknown Market Type: {} Market:'
                    .format(market.type, market))
