from django.test import TestCase
import mock

from ..views import CacheGetMixin


class MockBaseView(object):
    """Sets up `CacheGetMixin` to play wih a mock response object."""
    def get(self, request, **kwargs):
        class MockResponse(dict):
            def has_header(self, *args, **kwargs):
                return False
        return MockResponse()


class MockView(CacheGetMixin, MockBaseView):
    """Shim to test `CacheGetMixin`."""
    pass


class CacheGetMixinTest(TestCase):
    def test_it_works(self):
        # setup
        mock_request = mock.MagicMock()
        view = MockView()
        view.cache_control = {'max_age': 123}

        response = view.get(mock_request)
        self.assertEqual(response['Cache-Control'], 'max-age=123')
