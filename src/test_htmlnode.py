import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_to_html_raises(self):
        node = HTMLNode()
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_props_to_html_none(self):
        node = HTMLNode(props=None)
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_empty(self):
        node = HTMLNode(props={})
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_single_prop(self):
        node = HTMLNode(props={"href": "https://a.com"})
        self.assertEqual(node.props_to_html(), " href=https://a.com")

    def test_props_to_html_multiple_props(self):
        node = HTMLNode(props={"href": "https://a.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(), " href=https://a.com target=_blank")

    def test_repr(self):
        node = HTMLNode(
            tag="p", value="hello", children=None, props={"href": "https://a.com"}
        )
        self.assertEqual(
            repr(node), "HTMLNode(p, hello, None, {'href': 'https://a.com'})"
        )


if __name__ == "__main__":
    unittest.main()
