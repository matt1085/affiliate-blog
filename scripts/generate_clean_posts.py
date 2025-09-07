import os
import re

# Set paths
content_dir = os.path.expanduser("~/affiliate-blog/content")
posts = [
    {
        "title": "BigBlue 63W Foldable Solar Charger",
        "slug": "bigblue-63w-solar-charger",
        "category": "general",
        "date": "2025-09-04T22:31:09+00:00",
        "tags": ["solar","portable","outdoor","charger"],
        "featuredImage": "/images/bigblue-63w.jpg",
        "content": """
As outdoor enthusiasts, we know that our devices are always one step away from running out of juice...
"""
    },
    {
        "title": "Goal Zero Lighthouse Mini Core Lantern",
        "slug": "goal-zero-lantern",
        "category": "general",
        "date": "2025-09-04T22:35:02+00:00",
        "tags": ["light","portable","lantern","camping"],
        "featuredImage": "/images/goal-zero-lantern.jpg",
        "content": """
As outdoor enthusiasts, we know that a reliable light source is essential for any adventure...
"""
    }
    # Add the rest of your posts here, same format
]

for post in posts:
    folder = os.path.join(content_dir, post["category"])
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{post['slug']}.md")
    with open(file_path, "w") as f:
        f.write("+++\n")
        f.write(f'title = "{post["title"]}"\n')
        f.write(f'date = "{post["date"]}"\n')
        f.write(f'categories = ["{post["category"]}"]\n')
        tags_str = "[" + ", ".join(f'"{t}"' for t in post["tags"]) + "]"
        f.write(f"tags = {tags_str}\n")
        f.write(f'draft = false\n')
        f.write(f'featuredImage = "{post["featuredImage"]}"\n')
        f.write("+++\n\n")
        f.write(post["content"].strip())
