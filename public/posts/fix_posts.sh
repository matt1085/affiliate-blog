#!/bin/bash

for file in *.md; do
  # Remove duplicate front matter
  sed -i '/^+++$/,+1d' "$file"

  # Add correct front matter if missing
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
