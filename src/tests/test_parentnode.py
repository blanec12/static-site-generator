# import unittest
#
# from htmlnode import ParentNode, LeafNode
#
#
# class TestParentNode(unittest.TestCase):
#     def test_to_html_single_child(self):
#         node = ParentNode("p", [LeafNode("b", "Hello")])
#         self.assertEqual(node.to_html(), "<p><b>Hello</b></p>")
#
#     def test_to_html_multiple_children(self):
#         node = ParentNode(
#             "p",
#             [LeafNode("b", "Hello"), LeafNode(None, " "), LeafNode("i", "World")],
#         )
#         self.assertEqual(node.to_html(), "<p><b>Hello</b><i>World</i></p>")
#
#
# if __name__ == "__main__":
#     unittest.main()
