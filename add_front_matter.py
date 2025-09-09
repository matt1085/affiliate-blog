#!/usr/bin/env python3
import os
import csv
from datetime import datetime

# Paths
posts_dir = os.path.expanduser('~/affiliate-blog/content/posts/')
csv_file = os.path.expanduser('~/affiliate-blog/products.csv')

# Load product data from CSV
# CSV should have columns: asin,title,categories,tags,featuredImage
products = {}
with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        asin = row['asin'].lower()
        title = row.get('title', 'Untitled Product')
        categories = row.get('categories', 'General')
        tags = row.get('tags', '')
        featuredImage = row.get('featuredImage', '')
        products[asin] = {
            'title': title,
            'categories': [c.strip() for c in categories.split(',')] if categories else ['General'],
            'tags': [t.strip() for t in tags.split(',')] if tags else [],
            'featuredImage': featuredImage
        }

# Loop through all markdown files in posts_dir
for filename in os.listdir(posts_dir):
    if not filename.endswith(".md"):
        continue

    filepath = os.path.join(posts_dir, filename)
    asin = filename.replace('.md', '').lower()
    product = products.get(asin, None)

    # Default values if not in CSV
    title = product['title'] if product else "Untitled Product"
    categories = product['categories'] if product else ["General"]
    tags = product['tags'] if product else []
    featuredImage = product['featuredImage'] if product else ""

    # Read current content
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if front matter already exists
    if content.startswith("+++"):
        continue

    # Extract date from filename if possible (expects YYYY-MM-DD), else use today
    try:
        date_parts = filename.split('-')[0:3]  # ['YYYY','MM','DD']
        date_str = "-".join(date_parts) + "T02:00:00"
        datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")  # validate
    except Exception:
        date_str = datetime.now().strftime("%Y-%m-%dT02:00:00")

    # Build TOML front matter
    front_matter = "+++\n"
    front_matter += f'title = "{title}"\n'
    front_matter += f'date = {date_str}\n'
    front_matter += f'categories = {categories}\n'
    front_matter += f'tags = {tags}\n'
    front_matter += "draft = false\n"
    if featuredImage:
        front_matter += f'featuredImage = "{featuredImage}"\n'
    front_matter += "+++\n\n"

    # Write back new content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(front_matter + content)

print("✅ Front matter added to all markdown files (Kiera-compatible)!")
