#!/bin/bash
# Generate posts
python3 ~/affiliate-blog/ai_generate_posts.py

# Build Hugo site
hugo

# Go to repo
cd ~/affiliate-blog

# Only commit if there are changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    git add .
    git commit -m "Automated update: $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin main
    echo "$(date) - Changes pushed to GitHub" >> ~/affiliate-blog/auto_all.log
else
    echo "$(date) - No changes to commit" >> ~/affiliate-blog/auto_all.log
fi

