#!/bin/bash

# Set paths
POSTS_DIR=~/affiliate-blog/content/posts
IMG_DIR=~/affiliate-blog/static/images

mkdir -p "$IMG_DIR"
cd "$POSTS_DIR" || exit

for file in *.md; do
  echo "Processing $file …"
  slug=$(basename "$file" .md)

  # 1️⃣ Convert YAML front matter (---) to TOML (+++)
  if head -n 1 "$file" | grep -q "^---"; then
    sed -i '1s/^---$/+++/g' "$file"
    awk 'NR==1{print;next} /^---$/{print "+++";exit} {print}' "$file" > tmpfrontmatter
    tail -n +$(($(grep -n "^---" "$file" | tail -1 | cut -d: -f1)+1)) "$file" > tmpcontent
    cat tmpfrontmatter tmpcontent > tmpfile && mv tmpfile "$file"
    rm tmpfrontmatter tmpcontent
  fi

  # 2️⃣ Convert key: value -> key = value
  sed -i 's/^\([a-zA-Z0-9_]*\):[ ]*\(.*\)$/\1 = "\2"/' "$file"

  # 3️⃣ Add featuredImage if missing
  if ! grep -q "featuredImage" "$file"; then
    IMAGE_FILE="$IMG_DIR/${slug}.jpg"
    # Default to downloading from product URL if available
    AMAZON_URL=$(grep -oP '(?<=https://www\.amazon\.com/dp/)[A-Z0-9]+' "$file" | head -1)
    if [ -n "$AMAZON_URL" ]; then
      IMAGE_LINK="https://images-na.ssl-images-amazon.com/images/I/${AMAZON_URL}.jpg"
      echo "Downloading image for $slug …"
      curl -s -L -o "$IMAGE_FILE" "$IMAGE_LINK" || echo "Could not download image for $slug"
    fi
    # Add to front matter
    sed -i "1a featuredImage = \"/images/${slug}.jpg\"" "$file"
  fi
done

echo "✅ All posts converted, featured images added, and images downloaded!"
