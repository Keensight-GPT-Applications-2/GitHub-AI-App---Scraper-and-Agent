import os
import json
import re
import logging
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Initialize client
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
    timeout=30  # Added timeout
) if DEEPSEEK_API_KEY else None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("deepseek.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def generate_service_prompt(function_info: Dict[str, Any]) -> str:
    """Generate comprehensive prompt for microservice generation"""
    return f"""
    Generate a complete Python microservice definition including:
    1. Pydantic models for input/output
    2. FastAPI route implementation
    3. Error handling
    4. Documentation

    Follow this exact JSON format:
    {{
        "input_model": {{ "field_name": "type_hint" }},
        "output_model": {{ "field_name": "type_hint" }},
        "route_definition": {{
            "path": "/api/endpoint",
            "method": "POST",
            "summary": "Brief description"
        }},
        "example_usage": "curl example",
        "error_handling": [
            {{ "type": "HTTPError", "status_code": 400, "description": "Bad request" }}
        ]
    }}

    Function Details:
    - Name: {function_info['name']}
    - Parameters: {json.dumps(function_info['parameters'])}
    - Return Type: {function_info['return_type']}
    - Docstring: {function_info.get('docstring', 'No docstring available')}
    - Source Code: {function_info.get('source_code', '')[:1000]}...  # Truncated if long
    """

def normalize_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure consistent type hints in the response"""
    type_mapping = {
        "dict": "Dict[str, Any]",
        "list": "List[Any]",
        "None": "Optional[Any]",
        "Request": "HttpRequest"
    }
    
    def map_types(fields: Dict[str, Any]) -> Dict[str, Any]:
        return {k: type_mapping.get(v, v) for k, v in fields.items()}
    
    if "input_model" in response:
        response["input_model"] = map_types(response["input_model"])
    if "output_model" in response:
        response["output_model"] = map_types(response["output_model"])
    
    return response

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def query_deepseek(function_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Generate complete microservice definition from function details
    Args:
        function_info: {
            "name": str,
            "parameters": List[Dict[str, str]],  # [{"name": "param1", "type": "str"}]
            "return_type": str,
            "docstring": str,
            "source_code": str
        }
    """
    if not client:
        raise ValueError("DeepSeek client not initialized. Check API key.")
    
    try:
        # Build more contextual prompt
        prompt = f"""
        Analyze this Django view function and generate:
        1. Precise Pydantic models for request/response
        2. Field validation rules
        3. Example values
        
        Function: {function_info['name']}
        Parameters: {json.dumps(function_info['parameters'])}
        Return Type: {function_info['return_type']}
        Source Context: {function_info.get('source_code','')[:1000]}
        
        Respond ONLY with valid JSON in this format:
        {{
            "input_model": {{"field": "type"}},
            "output_model": {{"field": "type"}},
            "required_fields": ["field1"],
            "examples": {{
                "input": {{"field": "example"}},
                "output": {{"field": "example"}}
            }}
        }}
        """
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # More deterministic
            max_tokens=2000
        )
        
        if response.choices:
            raw_content = response.choices[0].message.content
            cleaned = re.sub(r"```json\n?(.*?)\n?```", r"\1", raw_content, flags=re.DOTALL)
            parsed = json.loads(cleaned.strip())
            return normalize_response(parsed)
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse response: {e}\nRaw content: {raw_content}")
    except Exception as e:
        logger.error(f"API request failed: {str(e)}")
    
    return None

if __name__ == "__main__":
    # Test with complete function info
    test_function = {
        "name": "process_user_data",
        "parameters": [
            {"name": "user_id", "type": "int"},
            {"name": "user_data", "type": "dict"}
        ],
        "return_type": "Dict[str, Any]",
        "docstring": "Process user data and return enriched information",
        "source_code": "def process_user_data(user_id: int, user_data: dict) -> dict:\n    ..."
    }
    
    result = query_deepseek(test_function)
    if result:
        print("Generated Microservice Definition:")
        print(json.dumps(result, indent=2))
    else:
        print("Failed to generate definition")