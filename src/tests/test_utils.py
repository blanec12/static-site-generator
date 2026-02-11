import unittest
from textnode import TextNode, TextType
from utils import (
    text_node_to_html_node,
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
    markdown_to_blocks,
    BlockType,
    block_to_block_type,
)


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


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_splits_single_code_span(self):
        node = TextNode("This is `code` text", TextType.PLAIN)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            result,
            [
                TextNode("This is ", TextType.PLAIN),
                TextNode("code", TextType.CODE),
                TextNode(" text", TextType.PLAIN),
            ],
        )

    def test_starts_with_delimited_text(self):
        node = TextNode("_italic_ after", TextType.PLAIN)
        result = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(
            result,
            [
                TextNode("italic", TextType.ITALIC),
                TextNode(" after", TextType.PLAIN),
            ],
        )

    def test_multiple_delimited_sections(self):
        node = TextNode("a `b` c `d` e", TextType.PLAIN)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            result,
            [
                TextNode("a ", TextType.PLAIN),
                TextNode("b", TextType.CODE),
                TextNode(" c ", TextType.PLAIN),
                TextNode("d", TextType.CODE),
                TextNode(" e", TextType.PLAIN),
            ],
        )

    def test_bold_delimiter(self):
        node = TextNode("a **b** c", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            result,
            [
                TextNode("a ", TextType.PLAIN),
                TextNode("b", TextType.BOLD),
                TextNode(" c", TextType.PLAIN),
            ],
        )

    def test_non_plain_nodes_pass_through_unchanged(self):
        nodes = [
            TextNode("already bold", TextType.BOLD),
            TextNode("and plain `code` here", TextType.PLAIN),
            TextNode("already italic", TextType.ITALIC),
        ]
        result = split_nodes_delimiter(nodes, "`", TextType.CODE)

        # bold and italic should remain untouched, only the plain node splits
        self.assertEqual(
            result,
            [
                TextNode("already bold", TextType.BOLD),
                TextNode("and plain ", TextType.PLAIN),
                TextNode("code", TextType.CODE),
                TextNode(" here", TextType.PLAIN),
                TextNode("already italic", TextType.ITALIC),
            ],
        )

    def test_unmatched_delimiter_raises(self):
        node = TextNode("broken `code span", TextType.PLAIN)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_no_delimiter_returns_original_text_node(self):
        node = TextNode("no code here", TextType.PLAIN)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [TextNode("no code here", TextType.PLAIN)])


class TestMarkdownExtraction(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_multiple(self):
        matches = extract_markdown_images(
            "![one](https://a.com/1.png) and ![two](https://b.com/2.jpg)"
        )
        self.assertListEqual(
            [
                ("one", "https://a.com/1.png"),
                ("two", "https://b.com/2.jpg"),
            ],
            matches,
        )

    def test_extract_markdown_images_none(self):
        matches = extract_markdown_images("This text has no images.")
        self.assertListEqual([], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev)"
        )
        self.assertListEqual([("to boot dev", "https://www.boot.dev")], matches)

    def test_extract_markdown_links_multiple(self):
        matches = extract_markdown_links(
            "[one](https://a.com) and [two](https://b.com)"
        )
        self.assertListEqual(
            [
                ("one", "https://a.com"),
                ("two", "https://b.com"),
            ],
            matches,
        )

    def test_extract_markdown_links_does_not_match_images(self):
        matches = extract_markdown_links(
            "![img](https://a.com/img.png) and [link](https://b.com)"
        )
        self.assertListEqual([("link", "https://b.com")], matches)


class TestSplitNodesImagesAndLinks(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_image([node])
        self.assertEqual(
            [
                TextNode("This is text with an ", TextType.PLAIN),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.PLAIN),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_images_no_images_returns_original(self):
        node = TextNode("Just plain text.", TextType.PLAIN)
        new_nodes = split_nodes_image([node])
        self.assertEqual([node], new_nodes)

    def test_split_images_non_plain_passes_through(self):
        node = TextNode("already bold", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        self.assertEqual([node], new_nodes)

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_link([node])
        self.assertEqual(
            [
                TextNode("This is text with a link ", TextType.PLAIN),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.PLAIN),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )

    def test_split_links_no_links_returns_original(self):
        node = TextNode("Just plain text.", TextType.PLAIN)
        new_nodes = split_nodes_link([node])
        self.assertEqual([node], new_nodes)

    def test_split_links_does_not_create_empty_text_nodes(self):
        node = TextNode(
            "[a](https://a.com)[b](https://b.com)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_link([node])
        self.assertEqual(
            [
                TextNode("a", TextType.LINK, "https://a.com"),
                TextNode("b", TextType.LINK, "https://b.com"),
            ],
            new_nodes,
        )


class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes_plain_only(self):
        text = "just plain text"
        self.assertEqual(
            [TextNode("just plain text", TextType.PLAIN)],
            text_to_textnodes(text),
        )

    def test_text_to_textnodes_bold_italic_code(self):
        text = "a **b** c _d_ e `f` g"
        self.assertEqual(
            [
                TextNode("a ", TextType.PLAIN),
                TextNode("b", TextType.BOLD),
                TextNode(" c ", TextType.PLAIN),
                TextNode("d", TextType.ITALIC),
                TextNode(" e ", TextType.PLAIN),
                TextNode("f", TextType.CODE),
                TextNode(" g", TextType.PLAIN),
            ],
            text_to_textnodes(text),
        )

    def test_text_to_textnodes_images_and_links(self):
        text = "start ![alt](https://img.com/a.png) mid " "[link](https://boot.dev) end"
        self.assertEqual(
            [
                TextNode("start ", TextType.PLAIN),
                TextNode("alt", TextType.IMAGE, "https://img.com/a.png"),
                TextNode(" mid ", TextType.PLAIN),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(" end", TextType.PLAIN),
            ],
            text_to_textnodes(text),
        )

    def test_text_to_textnodes_does_not_parse_links_inside_code(self):
        text = "pre `code [x](https://a.com)` post"
        self.assertEqual(
            [
                TextNode("pre ", TextType.PLAIN),
                TextNode("code [x](https://a.com)", TextType.CODE),
                TextNode(" post", TextType.PLAIN),
            ],
            text_to_textnodes(text),
        )

    def test_text_to_textnodes_adjacent_links_no_empty_plain_nodes(self):
        text = "[a](https://a.com)[b](https://b.com)"
        self.assertEqual(
            [
                TextNode("a", TextType.LINK, "https://a.com"),
                TextNode("b", TextType.LINK, "https://b.com"),
            ],
            text_to_textnodes(text),
        )

    def test_text_to_textnodes_adjacent_images_no_empty_plain_nodes(self):
        text = "![a](https://a.com/a.png)![b](https://b.com/b.png)"
        self.assertEqual(
            [
                TextNode("a", TextType.IMAGE, "https://a.com/a.png"),
                TextNode("b", TextType.IMAGE, "https://b.com/b.png"),
            ],
            text_to_textnodes(text),
        )


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks_single_block(self):
        md = "This is a single block"
        self.assertEqual(
            ["This is a single block"],
            markdown_to_blocks(md),
        )

    def test_markdown_to_blocks_multiple_blocks(self):
        md = "Block one\n\nBlock two\n\nBlock three"
        self.assertEqual(
            ["Block one", "Block two", "Block three"],
            markdown_to_blocks(md),
        )

    def test_markdown_to_blocks_strips_whitespace(self):
        md = "  Block one  \n\n   Block two\n\nBlock three   "
        self.assertEqual(
            ["Block one", "Block two", "Block three"],
            markdown_to_blocks(md),
        )

    def test_markdown_to_blocks_ignores_extra_blank_blocks(self):
        md = "Block one\n\n\n\nBlock two\n\n\n\n\n\nBlock three"
        self.assertEqual(
            ["Block one", "Block two", "Block three"],
            markdown_to_blocks(md),
        )

    def test_markdown_to_blocks_empty_string(self):
        md = ""
        self.assertEqual([], markdown_to_blocks(md))

    def test_markdown_to_blocks_only_whitespace(self):
        md = "   \n\n  \n\n"
        self.assertEqual([], markdown_to_blocks(md))


class TestBlockToBlockType(unittest.TestCase):
    def test_heading_h1(self):
        self.assertEqual(BlockType.HEADING, block_to_block_type("# Hello"))

    def test_heading_h6(self):
        self.assertEqual(BlockType.HEADING, block_to_block_type("###### Hello"))

    def test_heading_too_many_hashes_is_paragraph(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("####### Hello"))

    def test_heading_no_space_is_paragraph(self):
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type("#Hello"))

    def test_code_block_multiline(self):
        block = "```\ncode line 1\ncode line 2\n```"
        self.assertEqual(BlockType.CODE, block_to_block_type(block))

    def test_code_block_missing_newline_is_paragraph(self):
        block = "```code\n```"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))

    def test_quote_single_line(self):
        self.assertEqual(BlockType.QUOTE, block_to_block_type("> quote"))

    def test_quote_multiline(self):
        block = "> line1\n>line2\n> line3"
        self.assertEqual(BlockType.QUOTE, block_to_block_type(block))

    def test_quote_not_all_lines_are_quote_is_paragraph(self):
        block = "> line1\nline2"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))

    def test_unordered_list(self):
        block = "- a\n- b\n- c"
        self.assertEqual(BlockType.UNORDERED_LIST, block_to_block_type(block))

    def test_unordered_list_missing_space_is_paragraph(self):
        block = "-a\n-b"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))

    def test_ordered_list(self):
        block = "1. a\n2. b\n3. c"
        self.assertEqual(BlockType.ORDERED_LIST, block_to_block_type(block))

    def test_ordered_list_must_start_at_1(self):
        block = "2. a\n3. b"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))

    def test_ordered_list_must_increment_by_1(self):
        block = "1. a\n3. b"
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))

    def test_paragraph_default(self):
        block = "Just a normal paragraph\nwith two lines."
        self.assertEqual(BlockType.PARAGRAPH, block_to_block_type(block))


if __name__ == "__main__":
    unittest.main()
