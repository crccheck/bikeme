from django.test import TestCase


from ..factories import MarketFactory, StationFactory
# from ..models import *


class MarketTest(TestCase):
    def test_slug_is_auto_generated(self):
        market = MarketFactory()
        self.assertTrue(market.slug)


class StationTest(TestCase):
    def test_sandbox(self):
        station = StationFactory()
        self.assertTrue(station.market)
        self.assertIn(station, station.market.stations.all())
