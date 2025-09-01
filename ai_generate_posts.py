#!/bin/bash

# Log start
echo "$(date) - Starting automation" >> ~/affiliate-blog/auto_all.log

# 1. Generate posts with AI & updated affiliate links
python3 ~/affiliate-blog/ai_generate_posts.py >> ~/affiliate-blog/auto_all.log 2>&1

# 2. Build Hugo site
hugo >> ~/affiliate-blog/auto_all.log 2>&1

# 3. Commit & push if changes exist
cd ~/affiliate-blog || exit
if ! git diff --quiet || ! git diff --cached --quiet; then
    git add .
    git commit -m "Automated update: $(date '+%Y-%m-%d %H:%M:%S')" >> ~/affiliate-blog/auto_all.log 2>&1
    git push origin main >> ~/affiliate-blog/auto_all.log 2>&1
    echo "$(date) - Changes pushed to GitHub" >> ~/affiliate-blog/auto_all.log
else
    echo "$(date) - No changes to commit" >> ~/affiliate-blog/auto_all.log
fi

# 4. Optional: Email marketing (e.g., MailerLite)
python3 ~/affiliate-blog/send_email_updates.py >> ~/affiliate-blog/auto_all.log 2>&1
echo "$(date) - Email updates sent" >> ~/affiliate-blog/auto_all.log

echo "$(date) - Workflow finished" >> ~/affiliate-blog/auto_all.log

