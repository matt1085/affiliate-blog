#!/usr/bin/env python3
import csv
import os
from datetime import datetime
import requests
import json

# Paths
PRODUCTS_CSV = os.path.expanduser('~/affiliate-blog/products.csv')
CATEGORIES_CSV = os.path.expanduser('~/affiliate-blog/categories.csv')
CONTENT_DIR = os.path.expanduser('~/affiliate-blog/content/posts')

# Make sure content dir exists
os.makedirs(CONTENT_DIR, exist_ok=True)

# Load categories (optional)
categories_dict = {}
if os.path.exists(CATEGORIES_CSV):
    with open(CATEGORIES_CSV, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            categories_dict[row['asin']] = row.get('category', 'General')

# Generate affiliate link
def get_affiliate_link(asin, tag="matthewblog-20"):
    return f"https://www.amazon.com/dp/{asin}?tag={tag}"

# AI generation using Ollama
def generate_ai_content(prompt):
    url = "http://localhost:11434/api/generate"
    data = {"model": "llama3:8b", "prompt": prompt}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result_text = ''.join([r.get('response', '') for r in response.json() if 'response' in r])
        return result_text.strip()
    else:
        print(f"[x] AI generation failed: {response.status_code} {response.text}")
        return "AI content generation failed."

# Read products
with open(PRODUCTS_CSV, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        asin = row['asin'] if 'asin' in row else row.get('url', '').split('/dp/')[1].split('?')[0]
        post_file = os.path.join(CONTENT_DIR, f"{asin.lower()}.md")

        # Skip duplicates
        if os.path.exists(post_file):
            print(f"[i] Skipping existing post: {post_file}")
            continue

        title = row.get('title', asin)
        url = get_affiliate_link(asin)
        category = categories_dict.get(asin, 'General')

        # Prepare AI prompt
        prompt = f"Write a 150-200 word blog post for {title}. Include an engaging intro, benefits, and mention this link: {url}. Keep it natural and friendly."

        # Generate content
        content = generate_ai_content(prompt)

        # Write Hugo Markdown
        front_matter = f"---\ntitle: \"{title}\"\ndate: {datetime.now().isoformat()}\ncategories: [{category}]\n---\n\n"
        post_body = f"{content}\n\n[Buy {title}]({url})\n"

        with open(post_file, 'w') as f_post:
            f_post.write(front_matter + post_body)

        print(f"[+] Generated post: {post_file}")
