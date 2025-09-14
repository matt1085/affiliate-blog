import os
import re
import yaml

folder = './content/posts'  # change to your folder

for file in os.listdir(folder):
    if not file.endswith('.md'):
        continue
    path = os.path.join(folder, file)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract old front matter
    title = re.search(r'title\s*[:=]\s*“?(.+?)”?', content)
    date = re.search(r'date\s*[:=]\s*([0-9T:+-]+)', content)
    draft = re.search(r'draft\s*[:=]\s*(true|false)', content)
    categories = re.search(r'categories\s*[:=]\s*\[([^\]]+)\]', content)
    featured = re.search(r'featuredImage\s*[:=]\s*“(.+?)”', content)
    summary = re.search(r'summary\s*[:=]\s*“(.+?)”', content)

    # Remove old front matter lines
    content = re.sub(r'(?m)^(title|date|draft|categories|tags|featuredImage|summary)\s*[:=].*$', '', content).strip()

    # Build new YAML front matter
    fm = {}
    fm['title'] = title.group(1) if title else file.replace('.md','')
    fm['date'] = date.group(1) if date else '2025-09-09T00:00:00'
    fm['draft'] = draft.group(1).lower() == 'true' if draft else False
    if categories:
        fm['categories'] = [c.strip().strip('"') for c in categories.group(1).split(',')]
    if featured: fm['featuredImage'] = featured.group(1)
    if summary: fm['summary'] = summary.group(1)

    new_content = '---\n' + yaml.safe_dump(fm, sort_keys=False) + '---\n\n' + content
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Fixed {file}")
