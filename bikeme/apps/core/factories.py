import factory

from . import models


class MarketFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.Market
    name = factory.Sequence(lambda i: u'Market {}'.format(i))


class StationFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.Station
