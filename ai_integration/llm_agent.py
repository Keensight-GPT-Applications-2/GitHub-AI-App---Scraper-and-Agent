import os
from openai import OpenAI
from typing import Dict, Any

# Load DeepSeek API key from environment variable
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DeepSeek API key not found. Set the DEEPSEEK_API_KEY environment variable.")

# Initialize DeepSeek OpenAI-compatible client
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def generate_pydantic_schema_prompt(function_name: str, docstring: str, code: str) -> str:
    """
    Construct a prompt for the DeepSeek API to generate Pydantic input/output schemas
    based on the function name, docstring, and code.
    """
    prompt = f"""
You are an expert Python developer and Pydantic model generator.

Given the following Python function:

Function name: {function_name}

Docstring:
\"\"\"
{docstring}
\"\"\"

Function code:
\"\"\"
{code}
\"\"\"

Please generate:

1. A Pydantic BaseModel class named {function_name}Input that defines the input parameters with types and validations.
2. A Pydantic BaseModel class named {function_name}Output that defines the output schema based on the function's return value.

Provide only the Python code for these two classes, without any additional explanation or text.
"""
    return prompt

def call_deepseek_api(prompt: str) -> str:
    """
    Call DeepSeek API with the given prompt and return the response text.
    """
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates Pydantic models."},
            {"role": "user", "content": prompt}
        ],
        stream=False
    )
    return response.choices[0].message.content

def generate_models_from_llm(function_name: str, docstring: str, code: str) -> str:
    """
    Generate Pydantic models by calling the DeepSeek API with a constructed prompt.
    Returns the generated Python code as a string.
    """
    prompt = generate_pydantic_schema_prompt(function_name, docstring, code)
    return call_deepseek_api(prompt)
