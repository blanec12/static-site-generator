from textnode import TextType, TextNode
from htmlnode import ParentNode, LeafNode
import re
from enum import Enum
import textwrap
import os


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
    markdown = textwrap.dedent(markdown).strip()
    blocks = re.split(r"\n\s*\n", markdown)
    return [block.strip() for block in blocks if block.strip() != ""]


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def block_to_block_type(block):
    stripped_block = block.strip()

    if stripped_block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING

    if stripped_block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE

    lines = [line.strip() for line in stripped_block.split("\n")]

    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    if all(line.startswith(f"{i}. ") for i, line, in enumerate(lines, 1)):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        children.append(block_to_html_node(block))
    return ParentNode("div", children, None)


def block_to_html_node(block):
    block_type = block_to_block_type(block)
    match block_type:
        case BlockType.PARAGRAPH:
            return paragraph_to_html_node(block)
        case BlockType.HEADING:
            return heading_to_html_node(block)
        case BlockType.CODE:
            return code_to_html_node(block)
        case BlockType.QUOTE:
            return quote_to_html_node(block)
        case BlockType.UNORDERED_LIST:
            return unordered_list_to_html_node(block)
        case BlockType.ORDERED_LIST:
            return ordered_list_to_html_node(block)

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children

def paragraph_to_html_node(block):
    text = block.replace("\n", " ")
    children = text_to_children(text)
    return ParentNode("p", children)

def heading_to_html_node(block):
    level = len(block.split(" ")[0])
    text = block[level+1:]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)

def code_to_html_node(block):
    text = block[4:-3]
    text_node = TextNode(text, TextType.PLAIN)
    html_node = text_node_to_html_node(text_node)
    code = ParentNode("code", [html_node])
    return ParentNode("pre", [code])

def quote_to_html_node(block):
    lines = block.splitlines()
    cleaned_lines = [line[1:].strip() for line in lines]
    text = " ".join(cleaned_lines)
    children = text_to_children(text)
    return ParentNode("blockquote", children)

def unordered_list_to_html_node(block):
    items = block.splitlines()
    html_nodes = []
    for item in items:
        text = item.strip()[2:]
        child = text_to_children(text)
        html_nodes.append(ParentNode("li", child))
    return ParentNode("ul", html_nodes)


def ordered_list_to_html_node(block):
    items = block.splitlines()
    html_nodes = []
    for item in items:
        text = item.strip()[3:]
        child = text_to_children(text)
        html_nodes.append(ParentNode("li", child))
    return ParentNode("ol", html_nodes)

def extract_title(markdown):
    for line in markdown.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            title = line[1:].strip()
            return title
    raise ValueError("Could not extract title")

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r") as markdown_file:
        markdown = markdown_file.read()

    with open(template_path, "r") as template_file:
        template = template_file.read()

    title = extract_title(markdown)
    html_node = markdown_to_html_node(markdown)
    html = html_node.to_html()

    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html)

    with open(dest_path, "w") as dest_file:
        dest_file.write(template)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    os.makedirs(dest_dir_path, exist_ok=True)

    for entry in os.listdir(dir_path_content):
        content_entry_path = os.path.join(dir_path_content, entry)
        dest_entry_path = os.path.join(dest_dir_path, entry)

        if os.path.isfile(content_entry_path):
            if content_entry_path.endswith(".md"):
                html_dest_path = os.path.splitext(dest_entry_path)[0] + ".html"
                print(f"Generating page from {content_entry_path} to {html_dest_path}")
                generate_page(content_entry_path, template_path, html_dest_path)

        elif os.path.isdir(content_entry_path):
            print(f"Entering directory: {content_entry_path}")
            generate_pages_recursive(content_entry_path, template_path, dest_entry_path)
