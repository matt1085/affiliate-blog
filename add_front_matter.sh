#!/bin/bash

# Loop through all markdown files in content/posts
for file in ~/affiliate-blog/content/posts/*.md
do
  # Check if front matter already exists (starts with +++)
  first_line=$(head -n 1 "$file")
  if [ "$first_line" != "+++" ]; then
    # Add front matter at the top
    tmpfile=$(mktemp)
    echo "+++" > "$tmpfile"
    echo "title = \"$(basename "$file" .md | sed 's/-/ /g')\"" >> "$tmpfile"
    echo "date = 2025-09-04" >> "$tmpfile"
    echo "draft = false" >> "$tmpfile"
    echo "+++" >> "$tmpfile"
    echo "" >> "$tmpfile"
    cat "$file" >> "$tmpfile"
    mv "$tmpfile" "$file"
    echo "Front matter added to $file"
  else
    echo "Front matter already exists in $file"
  fi
done
