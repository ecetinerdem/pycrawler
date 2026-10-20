import asyncio
import sys
from crawl import crawl_page, get_html
from async_crawler import crawl_site_async
from json_report import write_json_report


async def main():
    if len(sys.argv) < 4:
        print("usage: main.py <base_url> <max_concurrency> <max_pages>")
        sys.exit(1)
    if len(sys.argv) > 4:
        print("too many arguments provided")
        sys.exit(1)

    base_url = sys.argv[1]
    try:
        max_concurrency = int(sys.argv[2])
        max_pages = int(sys.argv[3])
    except ValueError:
        print("max_concurrency and max_pages must be integers")
        sys.exit(1)

    print(f"starting crawl: {base_url}")

    page_data = await crawl_site_async(base_url, max_concurrency, max_pages)

    print(f"\nCrawl complete. Found {len(page_data)} pages.")

    write_json_report(page_data)
    print("Report written to report.json")


if __name__ == "__main__":
    asyncio.run(main())
