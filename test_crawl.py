import unittest
from json_report import write_json_report
from crawl import (
    normalize_url,
    get_heading_from_html,
    get_first_paragraph_from_html,
    get_urls_from_html,
    get_images_from_html,
    extract_page_data,
)


class TestCrawl(unittest.TestCase):
    def test_normalize_url_https_with_www(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_http_with_www(self):
        input_url = "http://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_no_scheme_no_www(self):
        input_url = "boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_https_no_www(self):
        input_url = "https://boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_http_no_www(self):
        input_url = "http://boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_h1(self):
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_h2_fallback(self):
        input_body = "<html><body><h2>Test Title</h2></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_h3_returns_empty(self):
        input_body = "<html><body><h3>Test Title</h3></body></html>"
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_no_heading_returns_empty(self):
        input_body = "<html><body><p>Test Title</p></body></html>"
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_without_p_fallback(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <h1>Main paragraph.</h1>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Outside paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_first_of_many(self):
        input_body = """<html><body>
            <main>
                <p>First paragraph.</p>
                <p>Second paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "First paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_no_paragraph_returns_empty(self):
        input_body = """<html><body>
            <main>
                <h1>First paragraph.</h1>
                <h2>Second paragraph.</h2>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = (
            '<html><body><a href="/path/one"><span>Boot.dev</span></a></body></html>'
        )
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/path/one"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_multiple_anchors(self):
        input_url = "https://crawler-test.com"
        input_body = """
        <html><body>
            <a href="/path/one">One</a>
            <a href="https://other.com/path/one">Two</a>
            <a href="/path/three">Three</a>
        </body></html>
        """
        actual = get_urls_from_html(input_body, input_url)
        expected = [
            "https://crawler-test.com/path/one",
            "https://other.com/path/one",
            "https://crawler-test.com/path/three",
        ]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_nested_anchors(self):
        input_url = "https://crawler-test.com"
        input_body = """
        <html><body>
            <nav><ul><li><a href="/a">A</a></li></ul></nav>
            <div><div><a href="/b">B</a></div></div>
        </body></html>
        """
        actual = get_urls_from_html(input_body, input_url)
        expected = [
            "https://crawler-test.com/a",
            "https://crawler-test.com/b",
        ]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="https://cdn.other.com/a.jpg"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://cdn.other.com/a.jpg"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_multiple_images(self):
        input_url = "https://crawler-test.com"
        input_body = """
        <html><body>
            <img src="/one.png">
            <div><img src="two.png"></div>
        </body></html>
        """
        actual = get_images_from_html(input_body, input_url)
        expected = [
            "https://crawler-test.com/one.png",
            "https://crawler-test.com/two.png",
        ]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_no_src_ignored(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img alt="no src"><img src="/ok.png"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/ok.png"]
        self.assertEqual(actual, expected)

    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "www.crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_empty_page(self):
        input_url = "https://crawler-test.com"
        input_body = "<html><body></body></html>"
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "www.crawler-test.com",
            "heading": "",
            "first_paragraph": "",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_fallbacks_and_mixed_urls(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <h2>Fallback Heading</h2>
            <main>
                <p>Main paragraph.</p>
            </main>
            <a href="/a">A</a>
            <a href="https://other.com/b">B</a>
            <img src="/1.png">
            <img src="https://cdn.other.com/2.png">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "www.crawler-test.com",
            "heading": "Fallback Heading",
            "first_paragraph": "Main paragraph.",
            "outgoing_links": [
                "https://crawler-test.com/a",
                "https://other.com/b",
            ],
            "image_urls": [
                "https://crawler-test.com/1.png",
                "https://cdn.other.com/2.png",
            ],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_relative_paths_resolve_against_page_url(self):
        input_url = "https://crawler-test.com/blog/post"
        input_body = """<html><body>
            <h1>Post</h1>
            <p>Post body.</p>
            <a href="next">Next</a>
            <img src="../img/pic.png">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "www.crawler-test.com/blog/post",
            "heading": "Post",
            "first_paragraph": "Post body.",
            "outgoing_links": ["https://crawler-test.com/blog/next"],
            "image_urls": ["https://crawler-test.com/img/pic.png"],
        }
        self.assertEqual(actual, expected)

    def test_write_json_report_sorted_by_url(self):
        import json
        import os
        import tempfile

        input_data = {
            "b": {"url": "www.b.com", "heading": "B"},
            "a": {"url": "www.a.com", "heading": "A"},
        }
        with tempfile.TemporaryDirectory() as tmp:
            filename = os.path.join(tmp, "report.json")
            write_json_report(input_data, filename)
            with open(filename, encoding="utf-8") as f:
                actual = json.load(f)
        expected = [
            {"url": "www.a.com", "heading": "A"},
            {"url": "www.b.com", "heading": "B"},
        ]
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
