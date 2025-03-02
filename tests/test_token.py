import requests
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Get token from environment
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

response = requests.get("https://api.github.com/user", headers=HEADERS)

if response.status_code == 200:
    print("✅ Token is valid! Logged in as:", response.json().get("login"))
else:
    print(f"❌ Token is invalid! Error {response.status_code}: {response.json()}")
