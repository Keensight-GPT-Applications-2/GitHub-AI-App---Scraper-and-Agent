import os
import re
from pydantic import BaseModel
from typing import Any, Optional
from pathlib import Path
from ai_integration.deepseek_api import query_deepseek
import json

def sanitize_function_name(name):
    """Sanitize function names to make them valid Python identifiers."""
    name = name.replace("__", "").capitalize()
    name = re.sub(r"[^0-9a-zA-Z_]", "", name)
    if not name.isidentifier():
        raise ValueError(f"Invalid function name: {name}")
    return name

def extract_models_from_response(response_content):
    """Extracts input and output models from DeepSeek response."""
    if isinstance(response_content, dict):  # ✅ Ensure it's a dictionary
        input_fields = response_content.get("input", {})
        output_type = response_content.get("output", "Optional[Any]")
        return input_fields, output_type
    else:
        print("⚠️ Unexpected response format from DeepSeek. Using default values.")
        return {}, "Optional[Any]"

def generate_pydantic_models(parsed_data):
    """
    Generate Pydantic input/output models with DeepSeek AI assistance.
    """
    models = []
    imports = """
from pydantic import BaseModel
from typing import Any, Optional
"""
    
    for file_name, content in parsed_data.items():
        for function in content["functions"]:
            safe_function_name = sanitize_function_name(function["name"])
            input_model_name = f"{safe_function_name}Input"
            output_model_name = f"{safe_function_name}Output"

            # **🧠 Ask DeepSeek for better input/output models**
            deepseek_prompt = (
                f"Generate a JSON response with 'input' and 'output' fields. "
                f"For function `{function['name']}` with parameters: {function['parameters']} "
                f"and return type: {function['return_type']}"
            )
            deepseek_response = query_deepseek(deepseek_prompt)

            if deepseek_response:
                input_fields, output_type = extract_models_from_response(deepseek_response)
            else:
                print(f"⚠️ DeepSeek failed for {function['name']}. Using default types.")
                input_fields = {param: "Any" for param in function["parameters"]}
                output_type = function["return_type"] or "Optional[Any]"

            # **Generate Input Model**
            input_model_fields = "\n".join([f"    {param}: {dtype}" for param, dtype in input_fields.items()])
            
            # **Generate Output Model**
            output_model_field = f"    result: {output_type} = None"
            
            # **Combine into a Model Code String**
            model_code = f"""
{imports}
class {input_model_name}(BaseModel):
{input_model_fields if input_model_fields else '    pass'}

class {output_model_name}(BaseModel):
{output_model_field}
"""
            models.append(model_code)
    
    return models

def save_pydantic_models(models, output_dir=None):
    """Save Pydantic models to github_scraper/models/generated_models/"""
    
    # ✅ Ensure the correct path relative to the project root
    project_root = Path(__file__).resolve().parent.parent  # Moves up from 'models'
    output_dir = project_root / "models/generated_models"  # ✅ Set to github_scraper/models/generated_models

    output_dir.mkdir(parents=True, exist_ok=True)

    for idx, model_code in enumerate(models, start=1):
        file_path = output_dir / f"model_{idx}.py"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f'"""\nAuto-generated Pydantic Models\nFile: {file_path.name}\n"""\n' + model_code.strip())
        
        print(f"✅ Model saved to {file_path}")

    print(f"📁 All models saved in: {output_dir}")

