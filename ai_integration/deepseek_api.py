import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any

# Load API Key from .env
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Initialize OpenAI-compatible client for DeepSeek
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def normalize_types(response_json: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize incorrect DeepSeek type responses (e.g., 'dict' -> 'Dict[str, Any]')."""
    type_map = {
        "dict": "Dict[str, Any]",
        "list": "List[Any]",
        "None": "Optional[Any]"
    }

    if "input" in response_json:
        response_json["input"] = {k: type_map.get(v, v) for k, v in response_json["input"].items()}
    
    if "output" in response_json:
        response_json["output"] = {k: type_map.get(v, v) for k, v in response_json["output"].items()}
    
    return response_json

def clean_json_response(raw_content: str) -> str:
    """
    Cleans the DeepSeek response by removing unnecessary Markdown code blocks.
    """
    # Remove markdown-style triple backticks (```json ... ```)
    raw_content = re.sub(r"```json\n(.*?)\n```", r"\1", raw_content, flags=re.DOTALL).strip()
    return raw_content

def query_deepseek(function_name: str, parameters: list, return_type: str):
    """Send a request to DeepSeek API and return a structured JSON response."""
    if not DEEPSEEK_API_KEY:
        raise ValueError("❌ DeepSeek API Key is missing. Add it to your .env file.")

    try:
        prompt = (
            "You are an AI that generates structured JSON for Python Pydantic models. "
            "Do not add explanations, only return JSON output in this exact format:\n\n"
            "{\n"
            '  "input": { "parameter_name": "actual_type" },\n'
            '  "output": { "return_value": "actual_type" }\n'
            "}\n\n"
            "Use valid Python types such as 'str', 'int', 'float', 'bool', 'Dict[str, Any]', or 'List[type]'. "
            "Ensure 'None' return types are represented as 'Optional[Any]'.\n\n"
            f"Function: `{function_name}`\n"
            f"Parameters: {parameters}\n"
            f"Return Type: {return_type}\n"
        )
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )

        # Extract and parse response safely
        if response and response.choices:
            raw_content = response.choices[0].message.content.strip()

            # ✅ Debugging Print Statement
            print(f"🔍 Raw DeepSeek Response: {raw_content}")

            # ✅ Ensure response is valid JSON
            try:
                cleaned_json = clean_json_response(raw_content)
                parsed_response = json.loads(cleaned_json)
                return normalize_types(parsed_response)
            except json.JSONDecodeError:
                print(f"❌ DeepSeek returned invalid JSON:\n{cleaned_json}")
                return None
        else:
            print("⚠️ DeepSeek returned an empty response.")
            return None

    except Exception as e:
        print(f"❌ DeepSeek API Error: {str(e)}")
        return None

# ✅ Test Function
if __name__ == "__main__":
    response = query_deepseek("AdminActivaUsers", ["request"], "None")
    print("🔍 DeepSeek Response:", response)
