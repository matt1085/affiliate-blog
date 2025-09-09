#!/bin/bash
# auto_push.sh - Automatic update and deployment of affiliate blog (Kiera-ready)

# Exit immediately if a command fails
set -e

# Log start time
LOGFILE="$HOME/affiliate-blog/logs/auto_push_$(date +'%Y%m%d').log"
mkdir -p "$HOME/affiliate-blog/logs"
echo "=== AUTO PUSH START: $(date) ===" >> "$LOGFILE"

# Go to project folder
cd ~/affiliate-blog

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "🟢 Virtual environment activated." | tee -a "$LOGFILE"
else
    echo "❌ Virtual environment not found. Please create .venv first." | tee -a "$LOGFILE"
    exit 1
fi

# Update product CSV
echo "🟢 Updating product CSV..." | tee -a "$LOGFILE"
python3 auto_fill_products_csv.py >> "$LOGFILE" 2>&1

# Generate new affiliate posts
echo "🟢 Generating new affiliate posts..." | tee -a "$LOGFILE"
python3 ai_generate_posts.py >> "$LOGFILE" 2>&1

# Add Kiera-compatible front matter
echo "🟢 Adding Kiera-compatible front matter..." | tee -a "$LOGFILE"
python3 add_front_matter.py >> "$LOGFILE" 2>&1

# Commit and push updates
echo "🟢 Committing and pushing updates to GitHub..." | tee -a "$LOGFILE"
git add content/posts/*.md
if git diff --cached --quiet; then
    echo "No changes to commit." | tee -a "$LOGFILE"
else
    git commit -m "Auto-update affiliate posts $(date +'%Y-%m-%d %H:%M')" >> "$LOGFILE" 2>&1
    git push origin main >> "$LOGFILE" 2>&1
fi

# Send email updates (optional)
echo "🟢 Sending email updates (optional)..." | tee -a "$LOGFILE"
python3 send_email_updates.py >> "$LOGFILE" 2>&1 || echo "⚠️ Email update failed (optional step)." | tee -a "$LOGFILE"

# Log end time
echo "✅ Auto-push complete! $(date)" | tee -a "$LOGFILE"
