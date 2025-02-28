import os
import re
import json
from pydantic import BaseModel
from typing import Any, Optional, Dict
from pathlib import Path
from ai_integration.deepseek_api import query_deepseek

def sanitize_function_name(name):
    """Sanitize function names to make them valid PascalCase class names."""
    name = re.sub(r"[^0-9a-zA-Z_]", "", name)  # Remove invalid characters
    name_parts = name.split("_")  # Split at underscores
    name = "".join(word.capitalize() for word in name_parts)  # Convert to PascalCase
    if not name.isidentifier():
        raise ValueError(f"Invalid function name: {name}")
    return name

def extract_models_from_response(response_content):
    """Extracts input and output models from DeepSeek response."""
    try:
        if isinstance(response_content, str):
            response_json = json.loads(response_content.strip("```json\n"))  
        elif isinstance(response_content, dict):
            response_json = response_content
        else:
            raise ValueError("Invalid response format from DeepSeek.")

        input_fields = response_json.get("input", {})
        output_type = response_json.get("output", {}).get("return_value", "Optional[Any]")

        input_fields = {key: "Dict[str, Any]" if val == "dict" else val for key, val in input_fields.items()}
        input_fields.pop("self", None)  
        input_fields.pop("selfself", None)  

        return input_fields, output_type

    except json.JSONDecodeError:
        print("❌ DeepSeek returned invalid JSON. Using default types.")
        return {}, "Optional[Any]"
    except ValueError as e:
        print(f"⚠️ Error processing DeepSeek response: {str(e)}")
        return {}, "Optional[Any]"

def generate_pydantic_models(parsed_data):
    """
    Generate Pydantic input/output models with function definitions.
    """
    models = {}
    imports = """from pydantic import BaseModel\nfrom typing import Any, Optional, Dict\nimport json\n"""

    for file_name, content in parsed_data.items():
        for function in content["functions"]:
            safe_function_name = sanitize_function_name(function["name"])
            input_model_name = f"{safe_function_name}Input"
            output_model_name = f"{safe_function_name}Output"

            try:
                deepseek_response = query_deepseek(
                    function["name"], function["parameters"], function["return_type"]
                )

                if deepseek_response:
                    input_fields, output_type = extract_models_from_response(deepseek_response)
                else:
                    raise ValueError("DeepSeek response invalid")

            except Exception:
                print(f"⚠️ DeepSeek failed for {function['name']}. Using default types.")
                input_fields = {param: "Any" for param in function["parameters"]}
                output_type = function["return_type"] or "Optional[Any]"

            input_model_fields = "\n".join([f"    {param}: {dtype}" for param, dtype in input_fields.items()])
            output_model_field = f"    result: {output_type} = None"

            # ✅ **Ensure function is included even if DeepSeek fails**
            function_code = f"""
def {function['name']}({', '.join(function['parameters'])}) -> {output_type}:
    \"\"\"{function['docstring'] if function['docstring'] else "No docstring provided."}\"\"\"
    import json  # Ensure json is imported in each function
    return {{'status': 'success', 'processed_data': json.dumps(request)}}"""

            model_code = f"""{imports}
class {input_model_name}(BaseModel):
{input_model_fields if input_model_fields else '    pass'}

class {output_model_name}(BaseModel):
{output_model_field}

{function_code.strip()}
"""

            models[safe_function_name] = model_code  

    return models

def save_pydantic_models(models, output_dir=None):
    """Save Pydantic models to github_scraper/models/generated_models/"""
    
    project_root = Path(__file__).resolve().parent.parent  
    output_dir = project_root / "models/generated_models"  

    output_dir.mkdir(parents=True, exist_ok=True)

    for model_name, model_code in models.items():
        file_path = output_dir / f"{model_name}.py"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f'"""\nAuto-generated Pydantic Model: {model_name}\n"""\n' + model_code.strip())
        
        print(f"✅ Model saved to {file_path}")

    print(f"📁 All models saved in: {output_dir}")
