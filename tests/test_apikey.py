import os
import requests

api_key = os.getenv("DEEPSEEK_API_KEY")
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.get("https://api.deepseek.com", headers=headers)

if response.status_code == 200:
    print("✅ DeepSeek API Key is valid!")
else:
    print(f"❌ API Key is invalid! Response: {response.text}")
