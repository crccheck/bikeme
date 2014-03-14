from dateutil.parser import parse
import requests

from .models import Market, Station, StationSnapshot


URL = 'http://bikeme-api.herokuapp.com/{market}/'


def update_market(market):
    response = requests.get(URL.format(market=market.slug))
    data = response.json()
    scraped_at = parse(data['now'])
    for row in data['results']:
        state, zip_code = row['state_zip'].split(' ', 2)
        defaults = dict(
            latitude=row['latitude'],
            longitude=row['longitude'],
            street=row['street'],
            zip=zip_code,
            state=state,
        )
        station, created = Station.objects.get_or_create(
            name=row['name'],
            market=market,
            defaults=defaults,
        )
        defaults = dict(
            bikes=row['bikes'],
            docks=row['docks'],
            status=row['status'],
        )
        ss, created = StationSnapshot.objects.get_or_create(
            timestamp=scraped_at,
            station=station,
            defaults=defaults,
        )


def update_all_markets():
    for market in Market.objects.all():
        update_market(market)
