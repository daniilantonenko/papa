import unittest

from utils import get_domain, get_response


class TestGetDomain(unittest.TestCase):
    def test_get_domain(self):
        url = 'https://example.com/path'
        expected_domain = 'example.com'
        self.assertEqual(get_domain(url), expected_domain)


class TestGetResponse(unittest.TestCase):
    def test_get_response(self):
        url = 'https://example.com'
        response = get_response(url)
        self.assertIsNotNone(response)