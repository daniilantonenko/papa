import unittest

from parser import BinaryTreeUrls


class TestBinaryTreeUrls(unittest.TestCase):
    def test_add_url(self):
        tree = BinaryTreeUrls()
        tree.add_url('https://example.com/path1/path2/path3/')
        tree.add_url('https://example.com/path1/path2/path4/')
        tree.add_url('https://example.com/path1/path5/path6/')
        tree.add_url('https://example.com/path1/path7/path8/')
        tree.add_url('https://example.com/path1/path9/path10/')

        tree_list  = tree.get_all_urls()

        expected_urls = [
            'https://example.com/path1/path2/path3/',
            'https://example.com/path1/path2/path4/',
            'https://example.com/path1/path5/path6/',
            'https://example.com/path1/path7/path8/',
            'https://example.com/path1/path9/path10/',
        ]
        self.assertEqual(tree_list, expected_urls)

    def test_get_all_exclude_urls(self):
        tree2 = BinaryTreeUrls()
        tree2.add_url('https://example.com/path1/path2/path3/')
        tree2.add_url('https://example.com/path1/path2/path4/')
        tree2.add_url('https://example.com/path1/path5/path6/')
        tree2.add_url('https://example.com/path1/path7/path8/')
        tree2.add_url('https://example.com/path1/path9/path10/')

        tree_list_2  = tree2.get_all_urls(exclude=1)

        expected_urls2 = [
            'https://example.com/path1/path2/path3/',
            'https://example.com/path1/path5/path6/',
            'https://example.com/path1/path7/path8/',
            'https://example.com/path1/path9/path10/',
        ]
        self.assertEqual(tree_list_2, expected_urls2)

    def test_get_all_exclude_urls_2(self):
        tree_3 = BinaryTreeUrls()
        tree_3.add_url('https://example.com/path1/path2/path3/')
        tree_3.add_url('https://example.com/path1/path2/path4/')
        tree_3.add_url('https://example.com/path1/path5/path6/')
        tree_3.add_url('https://example.com/path1/path7/path8/')
        tree_3.add_url('https://example.com/path1/path9/path10/')

        tree_list_3  = tree_3.get_all_urls(exclude=2)
        
        expected_urls_3 = [
            'https://example.com/path1/path2/path3/',
        ]
        self.assertEqual(tree_list_3, expected_urls_3)
