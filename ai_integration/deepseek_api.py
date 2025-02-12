import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API Key from .env
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Initialize OpenAI-compatible client for DeepSeek
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def query_deepseek(prompt: str):
    """Send a request to DeepSeek API and return a structured response."""
    if not DEEPSEEK_API_KEY:
        raise ValueError("❌ DeepSeek API Key is missing. Add it to your .env file.")

    try:
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )

        # ✅ Handle Empty Response
        if not response or not hasattr(response, "choices") or not response.choices:
            print("⚠️ DeepSeek returned an empty response.")
            return None

        # ✅ Extract Response Safely
        content = response.choices[0].message.content
        if not content:
            print("⚠️ DeepSeek response content is empty.")
            return None
        
        # ✅ Ensure JSON format
        try:
            response_json = json.loads(content)
            return response_json  # Ensure it returns a valid dictionary
        except json.JSONDecodeError:
            print("❌ DeepSeek returned invalid JSON. Falling back to default types.")
            return None

    except Exception as e:
        print(f"❌ DeepSeek API Error: {str(e)}")
        return None

# Test Function
if __name__ == "__main__":
    result = query_deepseek("What is 2+2?")
    if result:
        print(f"✅ Answer: {result.get('content')}")
    else:
        print("❌ No valid response received from DeepSeek.")
