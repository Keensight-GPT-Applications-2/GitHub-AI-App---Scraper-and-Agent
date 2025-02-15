import os
import re
import json
from pydantic import BaseModel
from typing import Any, Optional, Dict
from pathlib import Path
from ai_integration.deepseek_api import query_deepseek

def sanitize_function_name(name):
    """Sanitize function names to make them valid Python identifiers."""
    name = name.replace("__", "").capitalize()
    name = re.sub(r"[^0-9a-zA-Z_]", "", name)
    if not name.isidentifier():
        raise ValueError(f"Invalid function name: {name}")
    return name

def extract_models_from_response(response_content):
    """Extracts input and output models from DeepSeek response."""
    try:
        # ✅ Ensure response is a valid JSON dictionary
        if isinstance(response_content, str):
            response_json = json.loads(response_content.strip("```json\n"))  # Strips markdown artifacts
        elif isinstance(response_content, dict):
            response_json = response_content
        else:
            raise ValueError("Invalid response format from DeepSeek.")

        # ✅ Extract input and output safely
        input_fields = response_json.get("input", {})
        output_type = response_json.get("output", {}).get("return_value", "Optional[Any]")

        # ✅ Fix incorrect types (e.g., "dict" → "Dict[str, Any]")
        input_fields = {key: "Dict[str, Any]" if val == "dict" else val for key, val in input_fields.items()}

        # ✅ Remove problematic parameters
        input_fields.pop("self", None)  
        input_fields.pop("selfself", None)  

        return input_fields, output_type

    except json.JSONDecodeError:
        print("❌ DeepSeek returned invalid JSON. Falling back to default types.")
        return {}, "Optional[Any]"
    except ValueError as e:
        print(f"⚠️ Error processing DeepSeek response: {str(e)}")
        return {}, "Optional[Any]"

def generate_pydantic_models(parsed_data):
    """
    Generate Pydantic input/output models with DeepSeek AI assistance.
    """
    models = {}
    imports = """from pydantic import BaseModel\nfrom typing import Any, Optional, Dict\n"""

    for file_name, content in parsed_data.items():
        for function in content["functions"]:
            safe_function_name = sanitize_function_name(function["name"])
            input_model_name = f"{safe_function_name}Input"
            output_model_name = f"{safe_function_name}Output"

            # **🧠 Ask DeepSeek for better input/output models**
            deepseek_response = query_deepseek(
                function["name"], function["parameters"], function["return_type"]
            )

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
            model_code = f"""{imports}
class {input_model_name}(BaseModel):
{input_model_fields if input_model_fields else '    pass'}

class {output_model_name}(BaseModel):
{output_model_field}
"""

            models[safe_function_name.lower()] = model_code  # Use lowercase names for filenames

    return models

def save_pydantic_models(models, output_dir=None):
    """Save Pydantic models to github_scraper/models/generated_models/"""
    
    # ✅ Ensure the correct path relative to the project root
    project_root = Path(__file__).resolve().parent.parent  # Moves up from 'models'
    output_dir = project_root / "models/generated_models"  # ✅ Set to github_scraper/models/generated_models

    output_dir.mkdir(parents=True, exist_ok=True)

    for model_name, model_code in models.items():
        file_path = output_dir / f"{model_name}.py"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f'"""\nAuto-generated Pydantic Model: {model_name}\n"""\n' + model_code.strip())
        
        print(f"✅ Model saved to {file_path}")

    print(f"📁 All models saved in: {output_dir}")
