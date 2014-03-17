import json

from django.test import TestCase
import mock

from ..factories import MarketFactory
from ..utils import update_market_divvy


class TestDivvy(TestCase):
    def setUp(self):
        self.market = MarketFactory(type='divvy')
        with open('bikeme/apps/core/tests/support/divvy_response.json') as f:
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
        update_market_divvy(self.market)
        self.assertEqual(self.market.stations.count(), 300)

