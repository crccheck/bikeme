from django.test import TestCase

from ..factories import MarketFactory, StationFactory, SnapshotFactory
# from ..models import *


class MarketTest(TestCase):
    def test_slug_is_auto_generated(self):
        market = MarketFactory()
        self.assertTrue(market.slug)


class StationTest(TestCase):
    def test_sandbox(self):
        station = StationFactory()
        self.assertTrue(station.market)
        self.assertTrue(station.slug)
        self.assertIn(station, station.market.stations.all())


class SnapshotTest(TestCase):
    def test_sandbox(self):
        station = StationFactory()
        ss = SnapshotFactory(station=station)
        self.assertTrue(ss, station.history.all())
