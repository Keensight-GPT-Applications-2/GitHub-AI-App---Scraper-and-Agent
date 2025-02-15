from deepseek_api import query_deepseek
import json

# Test function query
response = query_deepseek("AdminLoginCheck", ["request"], "None")

print("\n🔍 DeepSeek Raw Response:")
print(response)

# Pretty-print JSON if it's valid
try:
    parsed_response = json.loads(response) if isinstance(response, str) else response
    print("\n✅ Parsed JSON Response:")
    print(json.dumps(parsed_response, indent=4))
except json.JSONDecodeError:
    print("❌ DeepSeek returned an invalid JSON format.")
