import os
import requests

API_KEY = os.getenv("MAILERLITE_API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

resp = requests.get("https://api.mailerlite.com/api/v2/groups", headers=HEADERS)
groups = resp.json()
for g in groups:
    print(g["id"], g["name"])
