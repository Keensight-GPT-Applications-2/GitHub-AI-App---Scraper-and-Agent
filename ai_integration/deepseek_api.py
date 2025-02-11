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
        messages = [{"role": "user", "content": prompt}]  # ✅ Ensure it's a list of dictionaries
        response = client.chat.completions.create(
            model="deepseek-chat",  # ✅ Use "deepseek-chat" to avoid errors
            messages=messages  # ✅ Pass as a list, not a string
        )

        # Extract response safely
        if response and response.choices:
            content = response.choices[0].message.content
            return {"content": content}
        else:
            print("⚠️ DeepSeek returned an empty response.")
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
