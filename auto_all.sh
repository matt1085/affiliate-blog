#!/bin/bash
# auto_generate_post.sh - generate an affiliate blog post using Ollama and push changes
set -euo pipefail

# --- Paths ---
BLOG_DIR="$HOME/affiliate-blog"
POSTS_DIR="$BLOG_DIR/content/posts"
MODEL="llama3:8b"  # adjust if you use a different model

mkdir -p "$POSTS_DIR"
cd "$BLOG_DIR"

# --- Filenames and dates ---
DATE_ISO=$(date -Iseconds)
DATE_SLUG=$(date +%Y-%m-%d-%H%M)
FILENAME="$POSTS_DIR/$DATE_SLUG-auto-post.md"

# --- Generate post title ---
TITLE=$(ollama run "$MODEL" "Give me a short, punchy 5-8 word blog post title about affordable home solar panels. Return only the title.")
TITLE_CLEAN=$(echo "$TITLE" | head -n1 | tr -d '\r')

# --- Generate post body in Markdown with placeholder for affiliate link ---
BODY=$(ollama run "$MODEL" "Write a 700-word SEO-friendly affiliate blog post in Markdown about affordable home solar panels. Include one placeholder [BUY_HERE] where the purchase link should go.")

# --- Write the post with Hugo/Kiera front matter ---
cat > "$FILENAME" <<EOF
+++
title = "$TITLE_CLEAN"
date = "$DATE_ISO"
draft = false
categories = ["Gear"]
tags = ["solar","renewable","home","guide"]
+++

$BODY
EOF

# --- Replace placeholder with your actual Amazon affiliate link ---
AFFILIATE_LINK="https://amzn.to/YOURAFFILIATEID"  # Replace with your real affiliate link
sed -i "s|\[BUY_HERE\]|$AFFILIATE_LINK|g" "$FILENAME"

echo "✅ Generated: $FILENAME"

# --- Build the site with Hugo ---
hugo

# --- Commit & push only if changes exist ---
git add .
if ! git diff --cached --quiet; then
  git commit -m "Automated post: $(date '+%Y-%m-%d %H:%M:%S')"
  git push origin main
  echo "$(date) - Changes pushed to GitHub" >> "$BLOG_DIR/logs/auto_all.log"
else
  echo "$(date) - No changes detected" >> "$BLOG_DIR/logs/auto_all.log"
fi
