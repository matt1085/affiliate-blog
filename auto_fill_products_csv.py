#!/usr/bin/env python3
import csv
import requests
from bs4 import BeautifulSoup
import os

# Path to your products CSV
PRODUCTS_CSV = os.path.expanduser('~/affiliate-blog/products.csv')

def extract_asin_title(url):
    """Scrape Amazon product page for ASIN and title"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        title_tag = soup.find(id="productTitle")
        title = title_tag.get_text(strip=True) if title_tag else "Unknown Product"
        try:
            asin = url.split("/dp/")[1].split("?")[0]
        except IndexError:
            asin = None
        return asin, title
    except Exception as e:
        print(f"[x] Failed to fetch {url}: {e}")
        return None, "Unknown Product"

# Read CSV and update missing info
rows = []
with open(PRODUCTS_CSV, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        if not row.get('asin') or not row.get('title'):
            url = row.get('url')
            if url:
                asin, title = extract_asin_title(url)
                if asin: row['asin'] = asin
                if title: row['title'] = title
        rows.append(row)

# Write updated CSV
with open(PRODUCTS_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("[✓] products.csv updated with ASINs and titles")
