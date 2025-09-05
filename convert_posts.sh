#!/bin/bash

cd ~/affiliate-blog/content/posts || exit

for file in *.md; do
  echo "Processing $file …"

  # Detect YAML front matter (---) and convert to TOML (+++)
  if head -n 1 "$file" | grep -q "^---"; then
    # Replace first --- with +++
    sed -i '1s/^---$/+++/g' "$file"
    # Replace ending --- with +++ (assume it’s the first --- after line 1)
    awk 'NR==1{print;next} /^---$/{print "+++";exit} {print}' "$file" > tmpfrontmatter
    tail -n +$(($(grep -n "^---" "$file" | tail -1 | cut -d: -f1)+1)) "$file" > tmpcontent
    cat tmpfrontmatter tmpcontent > tmpfile && mv tmpfile "$file"
    rm tmpfrontmatter tmpcontent
  fi

  # Remove any leftover YAML blocks (---) after TOML
  sed -i '/^---$/,+1d' "$file"

  # Fix key: value -> key = value in TOML
  sed -i 's/^\([a-zA-Z0-9_]*\):[ ]*\(.*\)$/\1 = \2/' "$file"

  # Add featuredImage at top if missing
  slug=$(basename "$file" .md)
  if ! grep -q "featuredImage" "$file"; then
    sed -i "1a featuredImage = \"/images/${slug}.jpg\"" "$file"
  fi
done

echo "All posts converted to TOML and featured images added!"

