#!/bin/bash

POSTS_DIR=~/affiliate-blog/content/posts
IMG_DIR=~/affiliate-blog/static/images

mkdir -p "$IMG_DIR"

for file in "$POSTS_DIR"/*.md; do
    slug=$(basename "$file" .md)
    url=$(grep -oP 'featuredImage\s*=\s*"\K[^"]+' "$file")
    if [[ -n "$url" ]]; then
        outfile="$IMG_DIR/$slug.jpg"
        if [[ ! -f "$outfile" ]]; then
            echo "Downloading $slug..."
            wget -q -O "$outfile" "$url"
        else
            echo "$slug already exists, skipping."
        fi
    fi
done

echo "All images processed!"
