#!/bin/bash
set -euo pipefail

BLOG_DIR="/home/elizabeth/affiliate-blog"
POSTS_DIR="$BLOG_DIR/content/posts"
MODEL="llama3:8b"  # adjust if you use a different model

mkdir -p "$POSTS_DIR"
cd "$BLOG_DIR"

DATE_ISO=$(date -Iseconds)
DATE_SLUG=$(date +%Y-%m-%d-%H%M)
FILENAME="$POSTS_DIR/$DATE_SLUG-auto-post.md"

# --- Make a title ---
TITLE=$(ollama run "$MODEL" "Give me a short, punchy 5-8 word blog post title about affordable home solar panels. Return ONLY the title, no quotes, no punctuation at the end.")
TITLE_CLEAN=$(echo "$TITLE" | head -n1 | tr -d '\r')

# --- Generate the body (Markdown, includes [BUY_HERE]) ---
BODY=$(ollama run "$MODEL" "Write a 700-word SEO-friendly affiliate blog post in Markdown about affordable home solar panels for beginners. Use headings (##, ###), bullet lists, and a comparison table. Include one call-to-action that uses the link placeholder [BUY_HERE] with anchor text 'Check price on Amazon'. Do not include YAML front matter.")

# --- Write the post with Hugo front matter ---
cat > "$FILENAME" <<EOF
---
title: "$TITLE_CLEAN"
date: $DATE_ISO
draft: false
tags: ["solar","renewable","home","guide"]
categories: ["Gear"]
---

$BODY
EOF

# --- Replace placeholder with your affiliate link ---
# TODO: replace YOURAFFILIATEID with your real Amazon shortlink or tag
sed -i 's|\[BUY_HERE\]|https://amzn.to/YOURAFFILIATEID|g' "$FILENAME"

echo "Generated: $FILENAME"

# --- Build the site ---
hugo

# --- Commit/push only if there are real changes ---
git add .
if ! git diff --cached --quiet; then
  git commit -m "Automated update: $(date '+%Y-%m-%d %H:%M:%S')"
  git push origin main
  echo "$(date) - Changes pushed to GitHub" >> "$BLOG_DIR/auto_all.log"
else
  echo "$(date) - No changes detected" >> "$BLOG_DIR/auto_all.log"
fi

