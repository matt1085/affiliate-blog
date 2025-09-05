#!/usr/bin/env python3
import csv
import os
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
from ai_generate_posts import generate_post_for_product  # your AI function

# Paths
PRODUCTS_CSV = os.path.expanduser('~/affiliate-blog/products.csv')
CONTENT_DIR = os.path.expanduser('~/affiliate-blog/content/posts')
os.makedirs(CONTENT_DIR, exist_ok=True)

# Affiliate tag
AFFILIATE_TAG = "matthewblog-20"

# Amazon URL list (can also load from a file)
AMAZON_URLS = [
    "https://www.amazon.com/Goal-Zero-Crush-Powered-Lantern/dp/B07BMJPH8L/",
    "https://www.amazon.com/Jackery-Portable-Explorer-Generator-Optional/dp/B082TMBYR6/",
    "https://www.amazon.com/EF-ECOFLOW-Portable-Charging-Generator/dp/B0B9XB57XM/",
    "https://www.amazon.com/Lichamp-Lanterns-Collapsible-Flashlight-Emergency/dp/B08WWX5GTZ/",
    "https://www.amazon.com/Anker-Foldable-Resistance-Ultra-Fast-Activities/dp/B0BX9FCSQQ/",
    "https://www.amazon.com/LuminAID-PackLite-Solar-Inflatable-Waterproof/dp/B0716JV1SG/",
    "https://www.amazon.com/BLUETTI-Portable-EB3A-Recharge-Generator/dp/B09WW3CTF4/",
    "https://www.amazon.com/Black-Diamond-Equipment-Lantern-Graphite/dp/B09NQL39X5/",
    "https://www.amazon.com/BigBlue-Charger-Digital-Waterproof-Foldable/dp/B071G4CQSR/",
    "https://www.amazon.com/Renogy-N-Type-16BB-Solar-Panel/dp/B0D3DZWXT4/",
    "https://www.amazon.com/Belkin-Portable-Charger-Output-Included/dp/B09NTNTVRJ/",
    "https://www.amazon.com/Jackery-SolarSaga-Bifacial-Portable-Explorer/dp/B0D5CCY5Y2/",
    "https://www.amazon.com/BigBlue-Foldable-Waterproof-SunPower-Cellphones/dp/B01EXWCPLC/",
    "https://www.amazon.com/Portable-Station-Foldable-Off-Grid-Monocrystalline/dp/B09W2CFT61/",
    "https://www.amazon.com/BLAVOR-Portable-Waterproof-Compatible-Backpacking/dp/B0BJDBQXQ3/",
    "https://www.amazon.com/FlexSolar-Portable-Waterproof-Foldable-Compatible/dp/B09H6GGK55/",
    "https://www.amazon.com/ALLPOWERS-Charger-Technology-Portable-Notebooks/dp/B075YRKVMH/",
    "https://www.amazon.com/Portable-Foldable-Efficiency-Dustproof-Backyard/dp/B0B7KY3D15/",
    "https://www.amazon.com/Renogy-Monocrystalline-Foldable-Waterproof-Controller/dp/B079JVBVL3/",
    "https://www.amazon.com/25000mAh-Hiluckey-Portable-Waterproof-Smartphones/dp/B07H8CM4F1/",
    "https://www.amazon.com/Jackery-Explorer-Portable-Generator-Emergency/dp/B0D7PPG25F/",
    "https://www.amazon.com/BLUETTI-Elite-100-V2-Generator/dp/B0F42CSQWG/",
    "https://www.amazon.com/Jackery-Explorer-Generator-Traveling-Emergencies/dp/B0CHVYPYD8/",
    "https://www.amazon.com/Goal-Zero-resistant-Dustproof-Tailgating/dp/B0CRDBGN2N/",
    "https://www.amazon.com/Anker-Generator-Portable-Batteries-Technology/dp/B0CBB6HFMM/",
    "https://www.amazon.com/EF-ECOFLOW-3600-4500W-Generator-Emergencies/dp/B0C1Z4GLKS/",
    "https://www.amazon.com/EF-ECOFLOW-Portable-Generator-Optional/dp/B0DCC2BVFW/",
    "https://www.amazon.com/Lighthouse-Functional-Adjustable-Emergency-Long-Lasting/dp/B08HRM4J8Y/",
    "https://www.amazon.com/Goal-Zero-Chroma-Powered-Lantern/dp/B07HFJH6D3/",
    "https://www.amazon.com/UST-30-Day-Lumen-Lantern-Titanium/dp/B07Q416Q8Z/",
    "https://www.amazon.com/Rechargeable-Portable-Cordless-Dimmable-Detachable/dp/B0BHN322QV/",
    "https://www.amazon.com/Primus-Micron-Lantern-Steel-Ignition/dp/B001QC78QK/",
    "https://www.amazon.com/Goal-Zero-Lighthouse-Flashlight-Recharger/dp/B075MGL7R8/",
    "https://www.amazon.com/BioLite-String-Rechargeable-Camping-44-Foot/dp/B0DXQQYF7X/"
]


# Category mapping
CATEGORY_KEYWORDS = {
    'Lantern': 'Camping',
    'Solar': 'Solar Power',
    'Generator': 'Generators',
    'Power Bank': 'Electronics',
    'Charger': 'Electronics',
}

FIELDNAMES = ["asin", "title", "category", "url"]

# --- Helpers ---
def extract_asin(url):
    """Extract ASIN from Amazon URL"""
    try:
        return re.search(r'/dp/([A-Z0-9]{10})', url).group(1)
    except:
        return None

def get_category(title):
    """Detect category based on keywords"""
    for keyword, cat in CATEGORY_KEYWORDS.items():
        if keyword.lower() in title.lower():
            return cat
    return "General"

def scrape_amazon_title(url, retries=3, delay=2):
    """Scrape Amazon product title with retries"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                title_tag = soup.find(id='productTitle')
                if title_tag:
                    return title_tag.get_text(strip=True)
            else:
                print(f"[!] Request failed ({r.status_code}) for {url}")
        except Exception as e:
            print(f"[!] Exception scraping {url}: {e}")
        time.sleep(delay)
    return None

# --- Load existing products ---
existing_products = {}
if os.path.exists(PRODUCTS_CSV):
    with open(PRODUCTS_CSV, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_products[row['asin']] = row

# --- Build products list ---
products = []
for url in AMAZON_URLS:
    asin = extract_asin(url)
    if not asin:
        print(f"[!] Could not extract ASIN from {url}")
        continue

    if asin in existing_products:
        print(f"[i] Skipping existing product: {asin}")
        products.append(existing_products[asin])
        continue

    title = scrape_amazon_title(url) or f"Product {asin}"
    category = get_category(title)
    product = {
        "asin": asin,
        "title": title,
        "category": category,
        "url": url
    }
    products.append(product)
    print(f"[✓] Added product: {title} ({asin})")
    time.sleep(1)  # polite pause

# --- Write products.csv safely ---
with open(PRODUCTS_CSV, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    for p in products:
        clean_dict = {k: p.get(k, "") for k in FIELDNAMES}
        writer.writerow(clean_dict)

print(f"[✓] products.csv updated with {len(products)} products")

# --- Generate AI posts for new products ---
for product in products:
    post_file = os.path.join(CONTENT_DIR, f"{product['asin'].lower()}.md")
    if os.path.exists(post_file):
        print(f"[i] Skipping existing post: {post_file}")
        continue
    print(f"[>] Generating AI post for {product['title']}")
    generate_post_for_product(product)  # AI handles writing markdown
    time.sleep(1)  # avoid overwhelming AI API
