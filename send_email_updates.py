#!/usr/bin/env python3
import os
import requests
import glob
import time

# -------------------------
# Configuration
# -------------------------
MAILERLITE_API_KEY = os.getenv("MAILERLITE_API_KEY")
OLLAMA_MODEL = "llama3:8b"  # default AI model
BLOG_URL = "https://youractualblog.com"  # replace with your blog URL
MAILER_GROUP_ID = 12345678  # replace with numeric group ID from step 1

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {MAILERLITE_API_KEY}"
}

OLLAMA_API_URL = "http://localhost:11434/api/generate"

# -------------------------
# Function: Generate summary using Ollama AI
# -------------------------
def generate_summary(post_content):
    data = {
        "model": OLLAMA_MODEL,
        "prompt": f"""Write a short, engaging email summary for the following blog post:

{post_content}

Keep it under 3 sentences, catchy and friendly.""",
        "max_tokens": 200
    }
    try:
        resp = requests.post(OLLAMA_API_URL, json=data, timeout=20)
        resp.raise_for_status()
        try:
            chunks = resp.json()
        except ValueError:
            print("[!] AI returned invalid JSON")
            return post_content[:200] + "..."
        text = ""
        if isinstance(chunks, list):
            for chunk in chunks:
                text += chunk.get("response", "")
        elif isinstance(chunks, dict):
            text = chunks.get("response", "")
        else:
            text = str(chunks)
        return text.strip()
    except Exception as e:
        print(f"[!] AI generation failed: {e}")
        return post_content[:200] + "..."  # fallback

# -------------------------
# Find newly generated posts
# -------------------------
posts = glob.glob("content/posts/*.md")
new_posts = [p for p in posts if not p.endswith(".sent.md")]

for post_file in new_posts:
    with open(post_file, "r") as f:
        content = f.read()

    summary = generate_summary(content)
    post_title = os.path.basename(post_file).replace(".md", "")
    post_url = f"{BLOG_URL}/{post_title}"

    # -------------------------
    # Create a MailerLite campaign
    # -------------------------
    campaign_payload = {
        "subject": f"New Blog Post: {post_title}",
        "from": {"email": "noreply@yourdomain.com", "name": "My Blog"},
        "groups": [MAILER_GROUP_ID],
        "html": f"<p>{summary}</p><p>Read more: <a href='{post_url}'>Click here</a></p>",
        "type": "regular"
    }

    try:
        resp = requests.post(
            "https://api.mailerlite.com/api/v2/campaigns",
            headers=HEADERS,
            json=campaign_payload,
            timeout=15
        )
        if resp.status_code not in [200, 201]:
            print(f"[!] Failed to create campaign for {post_file}: {resp.status_code} {resp.text}")
            continue

        campaign = resp.json()
        campaign_id = campaign.get("id")
        if not campaign_id:
            print(f"[!] No campaign ID returned for {post_file}")
            continue

        # Send the campaign
        send_resp = requests.post(
            f"https://api.mailerlite.com/api/v2/campaigns/{campaign_id}/send",
            headers=HEADERS,
            timeout=15
        )
        if send_resp.status_code in [200, 201]:
            print(f"[+] Email sent for {post_file}")
            os.rename(post_file, post_file.replace(".md", ".sent.md"))
            time.sleep(2)  # avoid rate limits
        else:
            print(f"[!] Failed to send campaign for {post_file}: {send_resp.status_code} {send_resp.text}")

    except Exception as e:
        print(f"[!] Error processing {post_file}: {e}")

