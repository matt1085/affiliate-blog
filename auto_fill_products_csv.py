#!/usr/bin/env python3
import csv
import requests
from bs4 import BeautifulSoup
import os

PRODUCTS_CSV = os.path.expanduser('~/affiliate-blog/products.csv')

def extract_asin_title_category(url):
    """Scrape Amazon product page for ASIN, title, and category"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")

        # Title
        title_tag = soup.find(id="productTitle")
        title = title_tag.get_text(strip=True) if title_tag else "Unknown Product"

        # ASIN
        try:
            asin = url.split("/dp/")[1].split("?")[0]
        except IndexError:
            asin = None

        # Category (from breadcrumb)
        category = "General"
        breadcrumb = soup.select("#wayfinding-breadcrumbs_feature_div ul li a")
        if breadcrumb:
            category = breadcrumb[-1].get_text(strip=True)

        return asin, title, category
    except Exception as e:
        print(f"[x] Failed to fetch {url}: {e}")
        return None, "Unknown Product", "General"

# Read CSV and update missing info
rows = []
with open(PRODUCTS_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        url = row.get('url')
        if url:
            if not row.get('asin') or not row.get('title') or not row.get('category'):
                asin, title, category = extract_asin_title_category(url)
                if asin: row['asin'] = asin
                if title: row['title'] = title
                if category: row['category'] = category
        rows.append(row)

# Write updated CSV
with open(PRODUCTS_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("[✓] products.csv updated with ASINs, titles, and categories")

