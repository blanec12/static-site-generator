import unittest

from htmlnode import ParentNode, LeafNode


class TestParentNode(unittest.TestCase):
    def test_to_html_single_child(self):
        node = ParentNode("p", [LeafNode("b", "Hello")])
        self.assertEqual(node.to_html(), "<p><b>Hello</b></p>")

    def test_to_html_multiple_children(self):
        node = ParentNode(
            "p",
            [LeafNode("b", "Hello"), LeafNode(None, " "), LeafNode("i", "World")],
        )
        self.assertEqual(node.to_html(), "<p><b>Hello</b> <i>World</i></p>")

    def test_to_html_nested_parents(self):
        inner = ParentNode("span", [LeafNode(None, "inside")])
        outer = ParentNode(
            "div", [LeafNode(None, "before "), inner, LeafNode(None, " after")]
        )
        self.assertEqual(outer.to_html(), "<div>before <span>inside</span> after</div>")

    def test_requires_tag(self):
        with self.assertRaises(ValueError) as cm:
            ParentNode(None, [LeafNode("b", "x")]).to_html()
        self.assertEqual(str(cm.exception), "All parent nodes must have a tag.")

    def test_requires_children(self):
        with self.assertRaises(ValueError) as cm:
            ParentNode("div", None).to_html()
        self.assertEqual(str(cm.exception), "All parent nodes must have children.")

        with self.assertRaises(ValueError) as cm:
            ParentNode("div", []).to_html()
        self.assertEqual(str(cm.exception), "All parent nodes must have children.")

    def test_propagates_child_errors(self):
        # LeafNode requires value; this should blow up inside parent's loop
        bad_child = LeafNode("b", None)
        node = ParentNode("p", [bad_child])

        with self.assertRaises(ValueError) as cm:
            node.to_html()
        self.assertEqual(str(cm.exception), "All leaf nodes must have a value.")


if __name__ == "__main__":
    unittest.main()
