#!/usr/bin/env python3
import os
import csv
import tomllib  # Python 3.11+
import argparse
from datetime import datetime

# --- CLI args ---
parser = argparse.ArgumentParser(description="Add & validate Hugo TOML front matter")
parser.add_argument("--fix", action="store_true", help="Auto-fix broken TOML by regenerating")
args = parser.parse_args()

# --- Paths ---
posts_dir = os.path.expanduser('~/affiliate-blog/content/posts/')
csv_file = os.path.expanduser('~/affiliate-blog/products.csv')

# --- Helpers ---
def clean_title(raw_title: str) -> str:
    if not raw_title:
        return "Untitled Product"
    title = raw_title.strip()
    if title.startswith('"') and title.endswith('"'):
        title = title[1:-1]
    if title.startswith("'") and title.endswith("'"):
        title = title[1:-1]
    return title.replace('"', "'")

def format_list(values) -> str:
    if not values:
        return "[]"
    return "[" + ", ".join(f'"{v}"' for v in values if v) + "]"

def extract_front_matter(content: str) -> str | None:
    if not content.startswith("+++"):
        return None
    parts = content.split("+++", 2)
    if len(parts) >= 2:
        return parts[1].strip()
    return None

def generate_front_matter(filename, product=None):
    title = clean_title(product['title']) if product else "Untitled Product"
    categories = product['categories'] if product else ["General"]
    tags = product['tags'] if product else []
    featuredImage = product['featuredImage'] if product else ""

    # Date extraction
    try:
        date_parts = filename.split('-')[0:3]
        date_str = "-".join(date_parts) + "T02:00:00Z"
        datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        date_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    # TOML
    fm = "+++\n"
    fm += f'title = "{title}"\n'
    fm += f'date = "{date_str}"\n'
    fm += f'categories = {format_list(categories)}\n'
    fm += f'tags = {format_list(tags)}\n'
    fm += "draft = false\n"
    if featuredImage:
        fm += f'featuredImage = "{featuredImage}"\n'
    fm += "+++\n\n"
    return fm

# --- Load CSV ---
products = {}
with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        asin = row['asin'].lower()
        products[asin] = {
            'title': clean_title(row.get('title', 'Untitled Product')),
            'categories': [c.strip() for c in row.get('categories', 'General').split(',')],
            'tags': [t.strip() for t in row.get('tags', '').split(',')],
            'featuredImage': row.get('featuredImage', '')
        }

# --- Process files ---
for filename in os.listdir(posts_dir):
    if not filename.endswith(".md"):
        continue
    filepath = os.path.join(posts_dir, filename)
    asin = filename.replace('.md', '').lower()
    product = products.get(asin, None)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if front matter already present
    if not content.startswith("+++"):
        fm = generate_front_matter(filename, product)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fm + content)
        continue

print("✅ Front matter ensured for all posts.")

# --- Validate ---
print("\n🔍 Validating TOML front matter...")
invalid_files = []
for filename in os.listdir(posts_dir):
    if not filename.endswith(".md"):
        continue

    filepath = os.path.join(posts_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    block = extract_front_matter(content)
    if not block:
        continue
    try:
        tomllib.loads(block)
    except Exception as e:
        invalid_files.append((filename, str(e)))

# --- Report / Fix ---
if invalid_files:
    print("\n❌ Found invalid TOML in these files:")
    for fname, err in invalid_files:
        print(f"   - {fname}: {err}")
    if args.fix:
        print("\n🛠 Fixing invalid TOML...")
        for fname, _ in invalid_files:
            filepath = os.path.join(posts_dir, fname)
            asin = fname.replace('.md', '').lower()
            product = products.get(asin, None)

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # strip broken block, regenerate
            parts = content.split("+++", 2)
            body = parts[2] if len(parts) >= 3 else content
            fm = generate_front_matter(fname, product)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fm + body)
        print("✅ Broken TOML fixed.")
else:
    print("✅ All TOML blocks are valid!")
