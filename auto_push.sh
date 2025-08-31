#!/bin/bash

# Full path to Hugo binary
HUGO_BIN="/snap/bin/hugo"

# Full path to your blog
BLOG_DIR="/home/elizabeth/affiliate-blog"

# Git settings
GIT_BRANCH="main"
GIT_REPO="git@github.com:matt1085/affiliate-blog.git"

# Move to blog directory
cd $BLOG_DIR || exit

# Build the site
$HUGO_BIN --minify

# Add changes to git
git add .

# Commit with timestamp
git commit -m "Automated update: $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null

# Push to remote
git push $GIT_REPO $GIT_BRANCH

