from textnode import TextType, TextNode
from htmlnode import LeafNode
import re
from enum import Enum


def text_node_to_html_node(text_node):
    match (text_node.text_type):
        case TextType.PLAIN:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
        case _:
            raise ValueError(f"Error: text type {text_node.text_type} does not exist.")


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.PLAIN)]
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


def extract_markdown_images(text):
    return re.findall(r"!\[([^\]]*)\]\(([^)\s]+)\)", text)


def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\]]+)\]\(\s*([^\s)]+)\s*\)", text)


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.PLAIN:
            new_nodes.append(node)
            continue

        parts = node.text.split(delimiter)

        if len(parts) % 2 == 0:
            raise ValueError(
                f"Invalid markdown syntax: unmatched delimiter '{delimiter}'"
            )

        for i, part in enumerate(parts):
            if part == "":
                continue

            if i % 2 == 0:
                # Outside delimiter - normal text
                new_nodes.append(TextNode(part, TextType.PLAIN))
            else:
                # Inside delimiter - special text
                new_nodes.append(TextNode(part, text_type))
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.PLAIN:
            new_nodes.append(node)
            continue

        text = node.text
        links = extract_markdown_links(text)

        if not links:
            new_nodes.append(node)
            continue

        for link_text, link_url in links:
            sections = text.split(f"[{link_text}]({link_url})", 1)
            before = sections[0]
            after = sections[1]

            if before:
                new_nodes.append(TextNode(before, TextType.PLAIN))

            new_nodes.append(TextNode(link_text, TextType.LINK, link_url))

            text = after

        if text:
            new_nodes.append(TextNode(text, TextType.PLAIN))

    return new_nodes


def split_nodes_image(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.PLAIN:
            new_nodes.append(node)
            continue

        text = node.text
        images = extract_markdown_images(text)

        if not images:
            new_nodes.append(node)
            continue

        for alt, src in images:
            sections = text.split(f"![{alt}]({src})", 1)
            before = sections[0]
            after = sections[1]

            if before:
                new_nodes.append(TextNode(before, TextType.PLAIN))

            new_nodes.append(TextNode(alt, TextType.IMAGE, src))

            text = after

        if text:
            new_nodes.append(TextNode(text, TextType.PLAIN))

    return new_nodes


def markdown_to_blocks(markdown):
    blocks = []
    lines = markdown.split("\n\n")
    for line in lines:
        line = line.strip()
        if line != "":
            blocks.append(line)
    return blocks


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def block_to_block_type(block):
    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING

    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE

    lines = block.split("\n")

    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    if all(line.startswith(f"{i}. ") for i, line, in enumerate(lines, 1)):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH
