#!/bin/bash

# Go to the blog folder
cd /home/elizabeth/affiliate-blog

# Build Hugo site
hugo

# Stage all changes
git add .

# Commit with a timestamp
git commit -m "Automated update: $(date '+%Y-%m-%d %H:%M:%S')"

# Push to GitHub
git push origin main
