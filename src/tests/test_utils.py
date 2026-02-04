import unittest
from textnode import TextNode, TextType
from utils import text_node_to_html_node


class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_plain_to_htmlnode(self):
        node = TextNode("hello", TextType.PLAIN)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "hello")
        self.assertEqual(html_node.props, None)

    def test_bold_to_leafnode(self):
        node = TextNode("bold", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "bold")
        self.assertEqual(html_node.props, None)

    def test_italic_to_leafnode(self):
        node = TextNode("italic", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "italic")
        self.assertEqual(html_node.props, None)

    def test_code_to_leafnode(self):
        node = TextNode("x = 1", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "x = 1")
        self.assertEqual(html_node.props, None)

    def test_link_to_leafnode(self):
        node = TextNode("boot.dev", TextType.LINK, "https://www.boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "boot.dev")
        self.assertEqual(html_node.props, {"href": "https://www.boot.dev"})

    def test_image_to_leafnode(self):
        node = TextNode("kitty", TextType.IMAGE, "https://img.com/cat.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props, {"src": "https://img.com/cat.png", "alt": "kitty"}
        )

    def test_unknown_type_raises_value_error(self):
        node = TextNode("something", "NOT_A_REAL_TYPE")
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)


if __name__ == "__main__":
    unittest.main()
