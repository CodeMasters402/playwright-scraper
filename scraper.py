"""
Browser-automation scraper (demo).

Loads https://books.toscrape.com/ in a real Chromium browser with
Playwright, waits for the catalogue to render, then extracts product
name, price, availability and detail-page URL — the same fields as the
plain-HTTP scraper in the ecommerce-product-scraper repo. It follows
the catalogue pagination and saves everything to products.csv.

Use a real browser like this when a site is JavaScript-heavy or blocks
plain HTTP requests: the page loads exactly as it would for a visitor.

Setup (once):
    pip install -r requirements.txt
    playwright install firefox

Run:
    python scraper.py
"""

import csv
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

BASE_URL = "https://books.toscrape.com/"
OUTPUT_FILE = "products.csv"


def extract_products(page):
    """Read the product rows currently shown on the catalogue page."""
    products = []
    for pod in page.locator("article.product_pod").all():
        link = pod.locator("h3 a")
        title = link.get_attribute("title").strip()
        # urljoin resolves the relative href against the current page URL.
        detail_url = urljoin(page.url, link.get_attribute("href"))
        price = pod.locator("p.price_color").inner_text().strip()
        availability = pod.locator("p.instock.availability").inner_text().strip()
        products.append(
            {
                "title": title,
                "price": price,
                "availability": availability,
                "url": detail_url,
            }
        )
    return products


def main():
    products = []
    pages = 0

    with sync_playwright() as p:
        # Firefox is used here because, in this environment, it works
        # through the network proxy where Chromium does not.
        browser = p.firefox.launch(headless=True)
        # ignore_https_errors is needed where a network proxy intercepts
        # TLS (common on corporate / cloud VMs); harmless elsewhere.
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        page.goto(BASE_URL, wait_until="domcontentloaded")
        # Wait until the catalogue has actually rendered.
        page.wait_for_selector("article.product_pod")

        while True:
            products.extend(extract_products(page))
            pages += 1
            print(f"Page {pages}: {len(products)} products so far...")
            next_link = page.locator("li.next a")
            if next_link.count() == 0:
                break
            # Wait for the URL to actually change: after a click,
            # wait_for_selector alone would return at once because the
            # old page's products are still in the DOM.
            old_url = page.url
            next_link.click()
            page.wait_for_url(lambda u: u != old_url)
            page.wait_for_selector("article.product_pod")

        browser.close()

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["title", "price", "availability", "url"]
        )
        writer.writeheader()
        writer.writerows(products)

    print(f"\nDone: {len(products)} products from {pages} pages.")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
