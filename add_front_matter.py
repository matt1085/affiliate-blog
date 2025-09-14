#!/usr/bin/env python3
import os
import csv
import tomllib  # Python 3.11+
import argparse
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# --- CLI args ---
parser = argparse.ArgumentParser(description="Add & validate Hugo TOML front matter")
parser.add_argument("--fix", action="store_true", help="Auto-fix broken TOML by regenerating")
args = parser.parse_args()

# --- Paths ---
base_dir = os.path.expanduser("~/affiliate-blog")
posts_dir = os.path.join(base_dir, "content/posts/")
csv_file = os.path.join(base_dir, "products.csv")
images_dir = os.path.join(base_dir, "static/images/")
placeholder_img = os.path.join(images_dir, "placeholder.jpg")

# --- Helpers ---
def clean_title(raw_title: str) -> str | None:
    """Normalize title string."""
    if not raw_title or raw_title.lower().startswith("product "):
        return None
    title = raw_title.strip().strip('"').strip("'")
    return title.replace('"', "'")

def format_list(values) -> str:
    """TOML array of strings."""
    return "[" + ", ".join(f'"{v}"' for v in values if v) + "]" if values else "[]"

def extract_front_matter(content: str) -> str | None:
    """Extract TOML block."""
    if not content.startswith("+++"):
        return None
    parts = content.split("+++", 2)
    return parts[1].strip() if len(parts) >= 2 else None

def fetch_amazon_title(asin: str) -> str | None:
    """Fetch product title from Amazon product page if missing."""
    url = f"https://www.amazon.com/dp/{asin}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            title_tag = soup.find(id="productTitle")
            if title_tag:
                return title_tag.text.strip()
    except Exception as e:
        print(f"⚠️ Failed to fetch title for {asin}: {e}")
    return None

def download_image(asin: str) -> str:
    """Download product image or use placeholder."""
    img_url = f"https://m.media-amazon.com/images/I/{asin}.jpg"
    img_path = os.path.join(images_dir, f"{asin}.jpg")
    if os.path.exists(img_path):
        return img_path
    try:
        r = requests.get(img_url, timeout=10)
        if r.status_code == 200:
            with open(img_path, "wb") as f:
                f.write(r.content)
            return img_path
        else:
            raise Exception(f"HTTP {r.status_code}")
    except Exception as e:
        print(f"⚠️ Failed to download image for {asin}: {e}")
        return placeholder_img

def generate_front_matter(filename, product=None):
    """Generate TOML front matter for a post."""
    asin = filename.replace(".md", "").upper()

    # Title
    title = clean_title(product["title"]) if product else None
    if not title:
        title = fetch_amazon_title(asin) or f"Untitled {asin}"

    # Categories / Tags
    categories = product["categories"] if product else ["General"]
    tags = product.get("tags", []) if product else []

    # Image
    img_path = download_image(asin) if product else placeholder_img

    # Date (try filename first)
    try:
        date_parts = filename.split("-")[0:3]
        date_str = "-".join(date_parts) + "T02:00:00Z"
        datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        date_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    # URL
    url = product.get("url") if product else f"https://www.amazon.com/dp/{asin}"

    # TOML front matter
    fm = "+++\n"
    fm += f'title = "{title}"\n'
    fm += f'date = "{date_str}"\n'
    fm += f'categories = {format_list(categories)}\n'
    fm += f'tags = {format_list(tags)}\n'
    fm += "draft = false\n"
    fm += f'featuredImage = "/images/{os.path.basename(img_path)}"\n'
    fm += f'url = "{url}"\n'
    fm += "+++\n\n"
    return fm

# --- Load CSV with case-insensitive headers ---
products = {}
if os.path.exists(csv_file):
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Lookup keys case-insensitively
            asin_key = next((k for k in row.keys() if k.lower() == "asin"), None)
            if not asin_key:
                continue
            asin = row[asin_key].lower()

            title_key = next((k for k in row.keys() if k.lower() == "title"), None)
            category_key = next((k for k in row.keys() if k.lower() == "category"), None)
            url_key = next((k for k in row.keys() if k.lower() == "url"), None)

            products[asin] = {
                "title": row.get(title_key, f"Untitled {asin}"),
                "categories": [row.get(category_key, "General")] if category_key else ["General"],
                "tags": [],
                "url": row.get(url_key, f"https://www.amazon.com/dp/{asin}")
            }

# --- Process posts ---
for filename in os.listdir(posts_dir):
    if not filename.endswith(".md"):
        continue
    filepath = os.path.join(posts_dir, filename)
    asin = filename.replace(".md", "").lower()
    product = products.get(asin)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("+++"):
        fm = generate_front_matter(filename, product)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(fm + content)

print("✅ Front matter ensured for all posts.")

# --- Validate TOML ---
print("\n🔍 Validating TOML front matter...")
invalid_files = []
for filename in os.listdir(posts_dir):
    if not filename.endswith(".md"):
        continue
    filepath = os.path.join(posts_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    block = extract_front_matter(content)
    if not block:
        continue
    try:
        tomllib.loads(block)
    except Exception as e:
        invalid_files.append((filename, str(e)))

if invalid_files:
    print("\n❌ Found invalid TOML in these files:")
    for fname, err in invalid_files:
        print(f"   - {fname}: {err}")
    if args.fix:
        print("\n🛠 Fixing invalid TOML...")
        for fname, _ in invalid_files:
            filepath = os.path.join(posts_dir, fname)
            asin = fname.replace(".md", "").lower()
            product = products.get(asin)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            parts = content.split("+++", 2)
            body = parts[2] if len(parts) >= 3 else content
            fm = generate_front_matter(fname, product)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(fm + body)
        print("✅ Broken TOML fixed.")
else:
    print("✅ All TOML blocks are valid!")
