#!/bin/bash
# Auto-generate blog posts with Ollama AI and insert affiliate links

BLOG_DIR="/home/elizabeth/affiliate-blog"
POSTS_DIR="$BLOG_DIR/content/posts"

cd "$BLOG_DIR" || exit

# Date-based filename
DATE=$(date +%Y-%m-%d)
FILENAME="$POSTS_DIR/$DATE-auto-post.md"

# Generate a 300-word SEO-friendly affiliate post with placeholders
ollama generate "Write a 300-word affiliate blog post in Markdown about solar panels. Use placeholder links like [BUY_HERE]. Add headings, lists, and images in Markdown format." > "$FILENAME"

# Replace placeholder with actual Amazon affiliate link
sed -i 's|\[BUY_HERE\]|https://amzn.to/YOURAFFILIATEID|g' "$FILENAME"

echo "Generated new post: $FILENAME"

