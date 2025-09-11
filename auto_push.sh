#!/bin/bash
# auto_push.sh - Automatic update and deployment of affiliate blog (Kiera-ready)

set -euo pipefail

# --- Setup logging ---
BASE_DIR="$HOME/affiliate-blog"
LOG_DIR="$BASE_DIR/logs"
LOGFILE="$LOG_DIR/auto_push_$(date +'%Y%m%d').log"
mkdir -p "$LOG_DIR"

echo "=== AUTO PUSH START: $(date) ===" | tee -a "$LOGFILE"

cd "$BASE_DIR"

# --- Virtual environment check ---
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "🟢 Virtual environment activated." | tee -a "$LOGFILE"
else
    echo "❌ Virtual environment not found at $BASE_DIR/.venv" | tee -a "$LOGFILE"
    exit 1
fi

# --- Step 1: Update product CSV ---
if [ -f "auto_fill_products_csv.py" ]; then
    echo "🟢 Updating product CSV..." | tee -a "$LOGFILE"
    python3 auto_fill_products_csv.py >> "$LOGFILE" 2>&1 || {
        echo "❌ Failed to update product CSV." | tee -a "$LOGFILE"
        exit 1
    }
fi

# --- Step 2: Generate new affiliate posts ---
if [ -f "ai_generate_posts.py" ]; then
    echo "🟢 Generating new affiliate posts..." | tee -a "$LOGFILE"
    python3 ai_generate_posts.py >> "$LOGFILE" 2>&1 || {
        echo "❌ Post generation failed." | tee -a "$LOGFILE"
        exit 1
    }
fi

# --- Step 3: Add Kiera-compatible front matter ---
if [ -f "add_front_matter.py" ]; then
    echo "🟢 Adding Kiera-compatible front matter..." | tee -a "$LOGFILE"
    python3 add_front_matter.py >> "$LOGFILE" 2>&1 || {
        echo "❌ Failed to add front matter." | tee -a "$LOGFILE"
        exit 1
    }
fi

# --- Step 4: Build the site (ensure Hugo output is valid) ---
if command -v hugo >/dev/null 2>&1; then
    echo "🟢 Building site with Hugo..." | tee -a "$LOGFILE"
    hugo >> "$LOGFILE" 2>&1 || {
        echo "❌ Hugo build failed." | tee -a "$LOGFILE"
        exit 1
    }
else
    echo "⚠️ Hugo not installed. Skipping build." | tee -a "$LOGFILE"
fi

# --- Step 5: Commit and push updates ---
echo "🟢 Committing and pushing updates to GitHub..." | tee -a "$LOGFILE"
git add content/posts/*.md >> "$LOGFILE" 2>&1 || true
git add . >> "$LOGFILE" 2>&1  # catch config changes, theme updates, etc.

if git diff --cached --quiet; then
    echo "No changes to commit." | tee -a "$LOGFILE"
else
    git commit -m "Auto-update affiliate posts $(date +'%Y-%m-%d %H:%M')" >> "$LOGFILE" 2>&1
    git push origin main >> "$LOGFILE" 2>&1
fi

# --- Step 6: Send email updates (optional) ---
if [ -f "send_email_updates.py" ]; then
    echo "🟢 Sending email updates..." | tee -a "$LOGFILE"
    python3 send_email_updates.py >> "$LOGFILE" 2>&1 || {
        echo "⚠️ Email update failed (optional)." | tee -a "$LOGFILE"
    }
fi

# --- Step 7: Log end ---
echo "✅ Auto-push complete! $(date)" | tee -a "$LOGFILE"

# --- Step 8: Rotate logs (keep last 7 days only) ---
find "$LOG_DIR" -type f -name "auto_push_*.log" -mtime +7 -delete
