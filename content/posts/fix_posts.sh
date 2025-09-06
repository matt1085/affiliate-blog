#!/bin/bash
# Fix Hugo posts front matter

for file in *.md; do
  # Extract first line that looks like a title, else fallback to filename
  title=$(grep -m1 "^title" "$file" | sed 's/title *= *//;s/[\"']//g')
  if [ -z "$title" ]; then
    title=$(basename "$file" .md)
  fi

  # Backup original
  cp "$file" "$file.bak"

  # Write clean front matter + body
  {
    echo "---"
    echo "title: \"$title\""
    echo "date: $(date -Iseconds)"
    echo "draft: false"
    echo "categories: [\"General\"]"
    echo "tags: []"
    echo "featuredImage: \"\""
    echo "summary: \"\""
    echo "---"
    echo
    # Append body without broken old front matter
    sed '/^title *=/d;/^date *=/d;/^draft *=/d;/^categories *=/d;/^tags *=/d;/^featuredImage *=/d;/^summary *=/d' "$file.bak"
  } > "$file"
done
