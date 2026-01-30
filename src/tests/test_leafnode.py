import unittest

from htmlnode import LeafNode


class TestLeafNode(unittest.TestCase):
    def test_to_html_no_tag(self):
        node = LeafNode(None, "just text")
        self.assertEqual(node.to_html(), "just text")

    def test_to_html_with_tag_no_props(self):
        node = LeafNode("p", "hello")
        self.assertEqual(node.to_html(), "<p>hello</p>")

    def test_to_html_with_props(self):
        node = LeafNode("a", "click", {"href": "https://a.com"})
        self.assertEqual(node.to_html(), "<a href=https://a.com>click</a>")

    def test_to_html_raises_no_value(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()

    def test_repr(self):
        node = LeafNode("a", "click", {"href": "https://a.com"})
        self.assertEqual(repr(node), "LeafNode(a, click, {'href': 'https://a.com'})")


if __name__ == "__main__":
    unittest.main()
