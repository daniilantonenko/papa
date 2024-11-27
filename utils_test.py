import unittest

from utils import get_domain, fetch_response


class TestGetDomain(unittest.TestCase):
    def test_get_domain(self):
        url = 'https://example.com/path'
        expected_domain = 'example.com'
        self.assertEqual(get_domain(url), expected_domain)


class TestFetchResponse(unittest.TestCase):
    def test_fetch_response(self):
        url = 'https://example.com'
        response = fetch_response(url)
        self.assertIsNotNone(response)