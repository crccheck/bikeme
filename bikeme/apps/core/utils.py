import logging

from dateutil.parser import parse
import requests

from .models import Market, Station, Snapshot


URL = 'http://bikeme-api.herokuapp.com/{market}/'

logger = logging.getLogger(__name__)


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
    response = requests.get(URL.format(market=market.slug))
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
    logger.info('Marking as inactive')


def update_market_divvy(market):
    status_lookup = {
        'In Service': 'available',
    }
    response = requests.get('divvybikes.com/stations/json/')
    data = response.json()
    scraped_at = parse(data['executionTime'])
    for row in data['stationBeanList']:
        defaults = dict(
            latitude=row['latitude'],
            longitude=row['latitude'],
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


def update_all_markets():
    for market in Market.objects.all():
        if market.type == 'bcycle':
            update_market_bcycle(market)
        else:
            logger.warn(u'Unknown Market Type: {} Market:'
                    .format(market.type, market))
