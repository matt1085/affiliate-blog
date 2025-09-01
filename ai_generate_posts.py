import csv
from datetime import datetime
import os

csv_file = os.path.expanduser("~/affiliate-blog/products.csv")
content_dir = os.path.expanduser("~/affiliate-blog/content/posts")

with open(csv_file, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        title = row['title']
        url = row['url']
        description = row['description']
        date = datetime.now().strftime("%Y-%m-%d")
        filename = f"{content_dir}/{title.replace(' ','_').lower()}.md"
        with open(filename, 'w') as md:
            md.write(f"---\n")
            md.write(f"title: \"{title}\"\n")
            md.write(f"date: {date}\n")
            md.write(f"draft: false\n")
            md.write(f"---\n\n")
            md.write(f"{{{{< affiliate title=\"{title}\" url=\"{url}\" >}}}}\n")
            md.write(f"{description}\n")
