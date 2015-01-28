from __future__ import division

import logging

from dateutil.parser import parse
from dateutil.tz import gettz
from django.db import IntegrityError
from project_runpy import ColorizingStreamHandler
import requests

from .models import Market, Station, Snapshot


logger = logging.getLogger(__name__)
logger.addHandler(ColorizingStreamHandler())


class AlreadyScraped(Exception):
    pass


def setfield(obj, fieldname, value):
    """Fancy setattr with debugging."""
    old = getattr(obj, fieldname)
    if hasattr(old, 'pk'):
        # foreign key comparison
        changed = old.pk != value.pk
    else:
        changed = str(old) != str(value)
    if changed:
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
            active=True,
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
        qs.update(active=False)
        logger.info('Marked stations as inactive', extra=dict(queryset=qs))


def update_market_alta(market):
    # http://www.altabicycleshare.com/locations
    lookup = {
        'bay-area': {
            'url': 'http://bayareabikeshare.com/stations/json/',
            'timezone': 'America/Los_Angeles',
        },
        'chattanooga': {
            'url': 'http://bikechattanooga.com/stations/json/',
            'timezone': 'America/New_York',
        },
        'chicago': {
            'url': 'http://www.divvybikes.com/stations/json/',
            'timezone': 'America/Chicago',
        },
        'nyc': {
            'url': 'http://citibikenyc.com/stations/json/',
            'timezone': 'America/New_York',
        },
    }
    status_lookup = {
        'In Service': 'active',
        'Not In Service': 'outofservice',
    }
    market_data = lookup[market.slug]
    response = requests.get(market_data['url'])
    data = response.json()
    tz = gettz(market_data['timezone'])
    scraped_at = parse(data['executionTime']).replace(tzinfo=tz)
    # see if we already scraped this before
    if Snapshot.objects.filter(station__market=market, timestamp=scraped_at).exists():
        raise AlreadyScraped()
    # pull all existing stations
    all_stations_lookup = {x.name: x for x in market.stations.all()}
    for row in data['stationBeanList']:
        station_defaults = dict(
            latitude=row['latitude'],
            longitude=row['longitude'],
            street=row['stAddress1'],
            zip=row['postalCode'][:5],
            capacity=row['totalDocks'],
            active=True,
            updated_at=scraped_at,
        )
        if row['stationName'] not in all_stations_lookup:
            station = Station.objects.create(
                name=row['stationName'],
                market=market,
                **station_defaults)
        else:
            station = all_stations_lookup[row['stationName']]
        # let this explode. If there's a duplicate, then we already scraped so
        # there's no need to scrape again
        snapshot = Snapshot.objects.create(
            timestamp=scraped_at,
            station=station,
            bikes=row['availableBikes'],
            docks=row['availableDocks'],
            status=status_lookup.get(row['statusValue'], 'outofservice'),
        )
        station_defaults['latest_snapshot'] = snapshot
        update_with_defaults(station, station_defaults)
    qs = market.stations.filter(updated_at__lt=scraped_at)
    if qs.exists():
        qs.update(active=False)
        logger.info('Marked stations as inactive', extra=dict(queryset=qs))


def update_market_citybikes(market):
    """Based on citybik.es api."""
    # TODO
    response = requests.get('http://api.citybik.es/{}.json')
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
        try:
            if market.type == 'bcycle':
                update_market_bcycle(market)
            elif market.type == 'alta':
                update_market_alta(market)
            else:
                logger.warn(u'Unknown Market Type: {} Market:'
                        .format(market.type, market))
        except AlreadyScraped:
            logger.exception()
