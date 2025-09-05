#!/bin/bash

cd ~/affiliate-blog/content/posts || exit

for file in *.md; do
  # Detect YAML front matter
  if head -n 1 "$file" | grep -q "^---"; then
    # Convert YAML (---) to TOML (+++)
    sed -i '1s/^---$/+++/g' "$file"
    # Convert end of front matter
    awk 'NR==1{print;next} /^---$/{print "+++";exit} {print}' "$file" > tmpfrontmatter
    # Extract rest of file
    tail -n +$(($(grep -n "^---" "$file" | tail -1 | cut -d: -f1)+1)) "$file" > tmpcontent
    # Merge back
    cat tmpfrontmatter tmpcontent > tmpfile && mv tmpfile "$file"
    rm tmpfrontmatter tmpcontent
  fi

  # Fix key: value -> key = value in TOML
  sed -i 's/^\([a-zA-Z0-9_]*\):[ ]*\(.*\)$/\1 = \2/' "$file"

  # Add featuredImage at top if missing
  slug=$(basename "$file" .md)
  if ! grep -q "featuredImage" "$file"; then
    sed -i "1a featuredImage = \"/images/${slug}.jpg\"" "$file"
  fi
done

echo "All posts converted to TOML and featured images added!"
