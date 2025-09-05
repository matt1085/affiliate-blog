#!/usr/bin/env python3
import csv
import os
from datetime import datetime
import requests
import time
import re

# Paths
PRODUCTS_CSV = os.path.expanduser('~/affiliate-blog/products.csv')
CATEGORIES_CSV = os.path.expanduser('~/affiliate-blog/categories.csv')
CONTENT_DIR = os.path.expanduser('~/affiliate-blog/content/posts')
os.makedirs(CONTENT_DIR, exist_ok=True)

# Load categories
categories_dict = {}
if os.path.exists(CATEGORIES_CSV):
    with open(CATEGORIES_CSV, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            categories_dict[row['asin']] = row.get('category', 'General')

# Affiliate tag
AFFILIATE_TAG = "matthewblog-20"

def get_affiliate_link(asin=None, url=None):
    """Return affiliate link for ASIN, or original URL if no ASIN."""
    if asin:
        return f"https://www.amazon.com/dp/{asin}?tag={AFFILIATE_TAG}"
    elif url:
        return url
    else:
        return "#"

def generate_ai_content(prompt, retries=3, wait=1):
    """Generate AI content using local LLaMA API with retry logic."""
    for attempt in range(retries):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3:8b", "prompt": prompt, "stream": False}
            )
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
        except Exception as e:
            print(f"[x] AI request error: {e}")
        print(f"[!] AI generation failed (attempt {attempt+1}/{retries}), retrying...")
        time.sleep(wait)
    return "AI content generation failed."

def safe_filename(name):
    """Convert title to safe filename for Markdown."""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name.replace(' ', '_')).lower()

def generate_post_for_product(product):
    """Generate a blog post for a single product dictionary."""
    asin = product.get('asin')
    url = product.get('url') or get_affiliate_link(asin=asin)
    title = product.get('title', f"Product {asin or 'Unknown'}")
    category = product.get('category', categories_dict.get(asin, 'General'))

    filename = safe_filename(asin or title)
    post_file = os.path.join(CONTENT_DIR, f"{filename}.md")

    if os.path.exists(post_file):
        print(f"[i] Skipping existing post: {post_file}")
        return

    prompt = f"""
Write a detailed 400-500 word blog post for '{title}'.
Include:
- Engaging introduction
- Key benefits or features
- Practical usage tips
- Call-to-action linking to the product
- Make it natural and friendly
Include the product link at the end: [Buy {title}]({url})
"""
    content = generate_ai_content(prompt)

    front_matter = f"""---
title: "{title}"
date: {datetime.now().isoformat()}
categories: ["{category}"]
---
"""
    post_body = f"{content}\n\n[Buy {title}]({url})\n"

    with open(post_file, 'w') as f_post:
        f_post.write(front_matter + post_body)

    print(f"[+] Generated post: {post_file}")

# Optional standalone run
if __name__ == "__main__":
    if os.path.exists(PRODUCTS_CSV):
        with open(PRODUCTS_CSV, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                generate_post_for_product(row)

