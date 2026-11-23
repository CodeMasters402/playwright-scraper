# Playwright Scraper

A browser-automation demo built with Playwright + Python. It loads [Books to Scrape](https://books.toscrape.com/) in a real browser, waits for the catalogue to render, extracts product name, price, availability and detail-page URL — the same fields as the plain-HTTP scraper in the `ecommerce-product-scraper` repo — follows the pagination, and saves everything to `products.csv`.

## Why a real browser?

Some sites are JavaScript-heavy: the data only appears after the page runs its scripts. Others block plain HTTP requests outright. A real browser loads the page exactly as a visitor sees it, so those sites can be scraped the same way.

## Setup

```bash
pip install -r requirements.txt
playwright install firefox
```

This demo uses Firefox: in some proxied environments Chromium cannot reach the network, while Firefox can.

## Run

```bash
python scraper.py
```

## Sample output

The full run collects 1,000 products from 50 pages. The first rows of `products.csv` look like this:

```csv
title,price,availability,url
A Light in the Attic,£51.77,In stock,https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
Tipping the Velvet,£53.74,In stock,https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html
Soumission,£50.10,In stock,https://books.toscrape.com/catalogue/soumission_998/index.html
```

The full `products.csv` is ignored by git (see `.gitignore`).

## How it works

1. Firefox opens the site headless and waits for `article.product_pod` to appear.
2. `extract_products` reads each product pod on the current page.
3. The "next" link is clicked, and the script waits for the page URL to actually change before reading again — otherwise it would re-read the old page.
4. Everything is written to `products.csv` with a short summary printed at the end.

Built by [CodeMasters](https://codemasters402.github.io/) — custom web scrapers, clean Excel/CSV data, fixed quote before starting.
