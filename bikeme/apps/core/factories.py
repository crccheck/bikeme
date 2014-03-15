import random

import factory
from django.utils import timezone
from faker import Factory

from . import models


fake = Factory.create()


class MarketFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.Market
    name = factory.Sequence(lambda i: u'Market {}'.format(i))


class StationFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.Station
    name = factory.Sequence(lambda i: u'Station {}'.format(i))
    market = factory.SubFactory(MarketFactory)
    latitude = factory.LazyAttribute(lambda __: fake.latitude())
    longitude = factory.LazyAttribute(lambda __: fake.longitude())
    street = factory.LazyAttribute(lambda __: fake.street_address())
    zip = factory.LazyAttribute(lambda __: fake.postcode())
    state = 'AA'
    updated_at = factory.LazyAttribute(lambda __: timezone.now())


class SnapshotFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.Snapshot
    station = factory.SubFactory(StationFactory)
    timestamp = factory.LazyAttribute(lambda __: timezone.now())
    bikes = factory.LazyAttribute(lambda __: random.randint(0, 10))
    docks = factory.LazyAttribute(lambda __: random.randint(0, 10))
