import json

from django.test import TestCase, TransactionTestCase
import mock

from ..factories import MarketFactory
from ..utils import (process_alta, process_bcycle, update_market_citybikes,
    AlreadyScraped)


class TestBcycle(TransactionTestCase):
    def setUp(self):
        self.market = MarketFactory(slug='bcycle')

    def test_it_works(self):
        with open('bikeme/apps/core/tests/support/austin_response1.json') as f:
            data = json.load(f)
        with self.assertNumQueries(362):
            process_bcycle(self.market, data)
        self.assertEqual(self.market.stations.count(), 45)
        # do it again
        with self.assertRaises(AlreadyScraped):
            process_bcycle(self.market, data)
        # assert number of stations did not change
        self.assertEqual(self.market.stations.count(), 45)


class TestAlta(TransactionTestCase):
    def setUp(self):
        self.market = MarketFactory(slug='chicago')

    def test_it_works(self):
        with open('bikeme/apps/core/tests/support/divvy_response1.json') as f:
            data = json.load(f)
        with self.assertNumQueries(1803):
            process_alta(self.market, data, 'America/Chicago')
        self.assertEqual(self.market.stations.count(), 300)
        # do it again
        with self.assertRaises(AlreadyScraped):
            process_alta(self.market, data, 'America/Chicago')
        # assert number of stations did not change
        self.assertEqual(self.market.stations.count(), 300)

    def test_it_updates(self):
        with open('bikeme/apps/core/tests/support/divvy_response1.json') as f:
            data = json.load(f)
        with self.assertNumQueries(1803):
            process_alta(self.market, data, 'America/Chicago')
        with open('bikeme/apps/core/tests/support/divvy_response2.json') as f:
            data = json.load(f)
        with self.assertNumQueries(1203):
            process_alta(self.market, data, 'America/Chicago')


class TestCityBikes(TestCase):
    def setUp(self):
        self.market = MarketFactory(type='citi')
        with open('bikeme/apps/core/tests/support/citi-bike-nyc.json') as f:
            data = json.load(f)
        mock_get = mock.MagicMock(name='mock_get',
                **{'json.return_value': data})
        mock_requests = mock.patch('bikeme.apps.core.utils.requests',
                **{'get.return_value': mock_get})
        mock_requests.start()
        self.mock_requests = mock_requests

    def tearDown(self):
        self.mock_requests.stop()

    def test_it_works(self):
        update_market_citybikes(self.market)
        self.assertEqual(self.market.stations.count(), 331)
        self.assertEqual(int(self.market.stations.all()[0].latitude), 40)
