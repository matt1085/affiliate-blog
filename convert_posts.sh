#!/bin/bash

cd ~/affiliate-blog/content/posts || exit

for file in *.md; do
  # Remove duplicate front matter blocks
  sed -i '/^+++$/,+1d' "$file"

  # Add fixed TOML front matter if missing or broken
  slug=$(basename "$file" .md)
  if ! grep -q "title" "$file"; then
    cat <<EOT > tmpfile
+++
title = "$slug"
date = $(date +%Y-%m-%dT%H:%M:%S)
categories = ["General"]
featuredImage = "/images/$slug.jpg"
draft = false
+++
EOT
    cat "$file" >> tmpfile
    mv tmpfile "$file"
  fi
done

echo "All posts cleaned and front matter fixed!"
