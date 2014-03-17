from django.test import TestCase

from ..factories import MarketFactory, StationFactory, SnapshotFactory
from ..models import Station


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

    def test_station_latest_snapshot(self):
        market = MarketFactory()
        for __ in range(9):
            # can have a latest snapshot
            station = StationFactory(market=market)
            station.latest_snapshot = SnapshotFactory(station=station)
            station.save()

        with self.assertNumQueries(1):
            qs = Station.objects.all().select_related('latest_snapshot')
            for x in qs:
                self.assertTrue(x.latest_snapshot)

    def test_get_score(self):
        station = StationFactory()
        self.assertEqual(station.get_score(), 0)
        SnapshotFactory(station=station)
        self.assertEqual(station.get_score(), 0)


class SnapshotTest(TestCase):
    def test_sandbox(self):
        station = StationFactory()
        ss = SnapshotFactory(station=station)
        self.assertTrue(ss, station.history.all())
