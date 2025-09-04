#!/usr/bin/env python3
import csv
import os
from datetime import datetime
import requests
import time

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

# Generate affiliate link
AFFILIATE_TAG = "matthewblog-20"
def get_affiliate_link(asin=None, url=None):
    if asin:
        return f"https://www.amazon.com/dp/{asin}?tag={AFFILIATE_TAG}"
    elif url:
        return url
    else:
        return "#"

# AI generation with retries
def generate_ai_content(prompt, retries=2):
    for _ in range(retries + 1):
        try:
            response = requests.post("http://localhost:11434/api/generate", json={"model": "llama3:8b", "prompt": prompt})
            if response.status_code == 200:
                result_text = ''.join([r.get('response', '') for r in response.json() if 'response' in r])
                if result_text.strip():
                    return result_text.strip()
        except Exception as e:
            print(f"[x] AI request error: {e}")
        print("[!] AI generation failed, retrying...")
        time.sleep(1)
    return "AI content generation failed."

# Read products and generate posts
with open(PRODUCTS_CSV, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        asin = row.get('asin', None)
        url = row.get('url', None)

        if not asin and url:
            # Extract ASIN from URL if present
            try:
                asin = url.split("/dp/")[1].split("?")[0]
            except IndexError:
                asin = None

        if not url:
            url = get_affiliate_link(asin=asin)

        title = row.get('title', f"Product {asin or 'Unknown'}")
        category = categories_dict.get(asin, 'General')
        post_file = os.path.join(CONTENT_DIR, f"{asin.lower() if asin else title.replace(' ','_')}.md")

        if os.path.exists(post_file):
            print(f"[i] Skipping existing post: {post_file}")
            continue

        # AI prompt
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

        # Hugo Markdown
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

