import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node1 = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node1, node2)

    def test_not_eq_different_text(self):
        node1 = TextNode("hello", TextType.BOLD)
        node2 = TextNode("goodbye", TextType.BOLD)
        self.assertNotEqual(node1, node2)

    def test_not_eq_different_text_type(self):
        node1 = TextNode("same text", TextType.PLAIN)
        node2 = TextNode("same text", TextType.BOLD)
        self.assertNotEqual(node1, node2)

    def test_eq_same_url(self):
        node1 = TextNode("link", TextType.LINK, "https://a.com")
        node2 = TextNode("link", TextType.LINK, "https://a.com")
        self.assertEqual(node1, node2)

    def test_not_eq_url_none_vs_set(self):
        node1 = TextNode("link", TextType.LINK)
        node2 = TextNode("link", TextType.LINK, "https://a.com")
        self.assertNotEqual(node1, node2)

    def test_not_eq_different_url(self):
        node1 = TextNode("link", TextType.LINK, "https://a.com")
        node2 = TextNode("link", TextType.LINK, "https://b.com")
        self.assertNotEqual(node1, node2)


if __name__ == "__main__":
    unittest.main()
