#!/bin/bash
# Auto-build Hugo site and push to GitHub

BLOG_DIR="/home/elizabeth/affiliate-blog"
cd "$BLOG_DIR" || exit

# Build the site
hugo

# Commit changes if there are any
git add .
if ! git diff --cached --quiet; then
    git commit -m "Automated update: $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin main
    echo "Site updated and pushed at $(date)" >> "$BLOG_DIR/auto_push.log"
else
    echo "No changes to push at $(date)" >> "$BLOG_DIR/auto_push.log"
fi

