import unittest
from utils import extract_markdown_images, extract_markdown_links


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


if __name__ == "__main__":
    unittest.main()
