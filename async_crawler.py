from urllib.parse import urljoin, urlparse, urlsplit
import asyncio
import aiohttp

from crawl import normalize_url, extract_page_data


async def crawl_site_async(base_url, max_concurrency=3, max_pages=25):
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()


class AsyncCrawler:
    def __init__(self, base_url, max_concurrency=3, max_pages=25):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.page_data = {}
        self.visited = set()
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.max_pages = max_pages
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session = None
        self.should_stop = False
        self.all_tasks = set()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if self.should_stop:
                return False

            if normalized_url in self.visited:
                return False

            if len(self.visited) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                return False

            self.visited.add(normalized_url)
            return True

    async def get_html(self, url):
        try:
            async with self.session.get(
                url, headers={"User-Agent": "BootCrawler/1.0"}
            ) as response:
                if response.status > 399:
                    print(f"Error: HTTP {response.status} for {url}")
                    return None

                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    print(f"Error: non-HTML content ({content_type}) for {url}")
                    return None

                return await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Error fetching {url}: {type(e).__name__} {e}")
            return None

    async def crawl_page(self, current_url):
        if self.should_stop:
            return

        if urlparse(current_url).netloc != self.base_domain:
            return

        normalized_url = normalize_url(current_url)

        if not await self.add_page_visit(normalized_url):
            return

        async with self.semaphore:
            print(f"Crawling now {current_url}")
            html = await self.get_html(current_url)
            if html is None:
                return
            extracted = extract_page_data(html, current_url)

        async with self.lock:
            self.page_data[normalized_url] = extracted

        tasks = []
        for next_url in extracted["outgoing_links"]:
            task = asyncio.create_task(self.crawl_page(next_url))
            self.all_tasks.add(task)
            tasks.append(task)

        try:
            await asyncio.gather(*tasks)
        finally:
            for task in tasks:
                self.all_tasks.discard(task)

    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data
