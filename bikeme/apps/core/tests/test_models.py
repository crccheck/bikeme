from django.test import TestCase


from ..factories import MarketFactory
# from ..models import *


class MarketTest(TestCase):
    def test_slug_is_auto_generated(self):
        market = MarketFactory()
        self.assertTrue(market.slug)
