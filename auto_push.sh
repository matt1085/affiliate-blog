#!/bin/bash

# --- CONFIG ---
HUGO_BIN="/snap/bin/hugo"
BLOG_DIR="/home/elizabeth/affiliate-blog"
GIT_BRANCH="main"
GIT_REPO="git@github.com:matt1085/affiliate-blog.git"
LOG_FILE="$BLOG_DIR/auto_push.log"

# --- GO TO BLOG DIRECTORY ---
cd "$BLOG_DIR" || exit

# --- BUILD THE SITE ---
$HUGO_BIN --minify >> "$LOG_FILE" 2>&1

# --- CHECK FOR CHANGES ---
git add .

if git diff --cached --quiet; then
    # No changes detected
    echo "$(date '+%Y-%m-%d %H:%M:%S') - No changes to commit" >> "$LOG_FILE"
else
    # Changes detected, commit and push
    git commit -m "Automated update: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1
    git push "$GIT_REPO" "$GIT_BRANCH" >> "$LOG_FILE" 2>&1
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Changes pushed to GitHub" >> "$LOG_FILE"
fi

