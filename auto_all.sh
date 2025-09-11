#!/bin/bash
# auto_generate_post.sh - generate an affiliate blog post using Ollama and push changes
set -euo pipefail

# --- Paths ---
BLOG_DIR="$HOME/affiliate-blog"
POSTS_DIR="$BLOG_DIR/content/posts"
LOG_DIR="$BLOG_DIR/logs"
MODEL="llama3:8b"  # adjust if you use a different model

mkdir -p "$POSTS_DIR" "$LOG_DIR"
cd "$BLOG_DIR"

# --- Filenames and dates ---
DATE_ISO=$(date -Iseconds)
DATE_SLUG=$(date +%Y-%m-%d-%H%M)
FILENAME="$POSTS_DIR/$DATE_SLUG-auto-post.md"
LOGFILE="$LOG_DIR/auto_all_$(date +'%Y%m%d').log"

# --- Error handling ---
trap 'echo "❌ Error at line $LINENO" >> "$LOGFILE"; exit 1' ERR

# --- Generate post title ---
TITLE=$(ollama run "$MODEL" "Give me a short, punchy 5-8 word blog post title about affordable home solar panels. Return ONLY the title, nothing else.")
TITLE_CLEAN=$(echo "$TITLE" | head -n1 | tr -d '\r')

# --- Generate post body in Markdown with placeholder for affiliate link ---
BODY=$(ollama run "$MODEL" "Write a 700-word SEO-friendly affiliate blog post in Markdown about affordable home solar panels. Include 3 section headers, a short intro and conclusion, and at least one [BUY_HERE] placeholder for the affiliate link.")

# --- Write the post with Hugo/Kiera front matter (TOML) ---
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

echo "✅ Generated: $FILENAME" | tee -a "$LOGFILE"

# --- Build the site with Hugo ---
if hugo >> "$LOGFILE" 2>&1; then
  echo "✅ Hugo build successful" | tee -a "$LOGFILE"
else
  echo "❌ Hugo build failed" | tee -a "$LOGFILE"
  exit 1
fi

# --- Commit & push only if changes exist ---
git add .
if ! git diff --cached --quiet; then
  git commit -m "Automated post: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOGFILE" 2>&1
  git push origin main >> "$LOGFILE" 2>&1
  echo "$(date) - Changes pushed to GitHub" | tee -a "$LOGFILE"
else
  echo "$(date) - No changes detected" | tee -a "$LOGFILE"
fi
