#!/bin/bash

# Stop on any error
set -e

echo "✅ Starting full Hugo module reset for Kiera theme..."

# 1. Remove Hermit theme folder
echo "1. Removing Hermit theme folder..."
rm -rf themes/hermit

# 2. Remove old Hugo module caches
echo "2. Removing old Hugo module caches..."
rm -rf resources/_gen modules

# 3. Remove module metadata files
echo "3. Removing module metadata files..."
rm -f modules.toml go.mod go.sum

# 4. Remove Hermit references from config.toml
echo "4. Cleaning config.toml from Hermit references..."
sed -i '/hermit/d' config.toml
sed -i 's/^theme\s*=.*/theme = "kiera"/' config.toml

# 5. Remove any nested Hermit references (optional, if config folder exists)
if [ -d "config" ]; then
    echo "5. Removing Hermit references in nested config folder..."
    grep -Rl hermit config/ | xargs -r sed -i '/hermit/d'
fi

# 6. Initialize Hugo modules for this site
echo "6. Initializing Hugo modules..."
hugo mod init github.com/matt1085/affiliate-blog

# 7. Fetch Kiera dependencies only
echo "7. Tidying Hugo modules..."
hugo mod tidy

# 8. Clean Hugo cache
echo "8. Cleaning Hugo cache..."
hugo mod clean

# 9. Build the site
echo "9. Building site..."
hugo --minify --ignoreCache --cleanDestinationDir

echo "✅ Done! The site should now build using Kiera theme only."
