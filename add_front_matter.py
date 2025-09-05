import os
import csv

# Path to posts and products.csv
posts_dir = os.path.expanduser('~/affiliate-blog/content/posts/')
csv_file = os.path.expanduser('~/affiliate-blog/products.csv')

# Load product titles from CSV (using ASIN as filename)
products = {}
with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        asin = row['asin'].lower()
        title = row['title']
        products[asin] = title

# Loop through all markdown files in posts_dir
for filename in os.listdir(posts_dir):
    if filename.endswith(".md"):
        filepath = os.path.join(posts_dir, filename)
        asin = filename.replace('.md','').lower()
        title = products.get(asin, "Untitled Product")

        # Read current content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skip if front matter already exists
        if content.startswith("+++"):
            continue

        # Add front matter
        front_matter = f"+++\ntitle = \"{title}\"\ndate = 2025-09-04\ndraft = false\n+++\n\n"
        new_content = front_matter + content

        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

print("Front matter added to all markdown files!")
