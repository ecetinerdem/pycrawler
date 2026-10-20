from re import error
from urllib.parse import urljoin, urlparse, urlsplit
from bs4 import BeautifulSoup, Tag
import requests
from typing import TypedDict


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


def get_html(url):

    response = requests.get(
        url,
        headers={"User-Agent": "BootCrawler/1.0"},
    )

    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")

    if not content_type.startswith("text/html"):
        raise ValueError(f"Expected text/html, got {content_type}")

    return response.text


def normalize_url(url: str) -> str:
    if not url:
        return ""

    if "//" not in url:
        url = f"//{url}"

    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    path = parts.path.rstrip("/")

    if host.count(".") == 1:
        host = "www." + host

    return f"{host}{path}"


def _text_of(tag) -> str:
    return tag.get_text(strip=True) if isinstance(tag, Tag) else ""


def get_heading_from_html(html: str) -> str:
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    return _text_of(soup.find("h1") or soup.find("h2"))


def get_first_paragraph_from_html(html: str) -> str:
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    p = (main.find("p") if isinstance(main, Tag) else None) or soup.find("p")
    return _text_of(p)


def get_urls_from_html(html, base_url):

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href")
        if isinstance(href, str) and href.strip():
            urls.append(urljoin(base_url, href.strip()))
    return urls


def get_images_from_html(html, base_url):
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for image in soup.find_all("img"):
        src = image.get("src")
        if isinstance(src, str) and src.strip():
            images.append(urljoin(base_url, src.strip()))
    return images


def extract_page_data(html: str, page_url: str) -> PageData:
    return {
        "url": normalize_url(page_url),
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }


def crawl_page(base_url, current_url=None, page_data=None):
    if current_url is None:
        current_url = base_url
    if page_data is None:
        page_data = {}

    if urlparse(base_url).netloc != urlparse(current_url).netloc:
        return page_data

    normalized_current_url = normalize_url(current_url)

    if normalized_current_url in page_data:
        return page_data

    print(f"Crawling now {current_url}")

    try:
        html = get_html(current_url)
    except Exception as e:
        print(f"Error crawling {current_url}: {e}")
        return page_data

    extracted_page_data = extract_page_data(html, current_url)
    page_data[normalized_current_url] = extracted_page_data

    for next_url in extracted_page_data["outgoing_links"]:
        crawl_page(base_url, next_url, page_data)

    return page_data
