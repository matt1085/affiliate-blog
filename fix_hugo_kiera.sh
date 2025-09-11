#!/bin/bash

# Stop on any error
set -e

echo "1. Removing Hermit theme folder..."
rm -rf themes/hermit

echo "2. Removing old Hugo module caches..."
rm -rf resources/_gen modules

echo "3. Removing module metadata files..."
rm -f modules.toml go.mod go.sum

echo "4. Ensuring config.toml points to Kiera theme..."
sed -i 's/^theme\s*=.*/theme = "kiera"/' config.toml

echo "5. Initializing Hugo modules for this site..."
hugo mod init github.com/matt1085/affiliate-blog

echo "6. Tidying Hugo modules (fetch Kiera dependencies only)..."
hugo mod tidy

echo "7. Cleaning Hugo cache..."
hugo mod clean

echo "8. Building the site..."
hugo --minify --ignoreCache --cleanDestinationDir

echo "✅ Done! Site should now build using Kiera theme only."
