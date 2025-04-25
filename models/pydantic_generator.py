import importlib
import os
import re
import json
from pydantic import BaseModel, Field
from typing import Any, Callable, Optional, Dict, List, Union
from pathlib import Path
from datetime import datetime
from ai_integration.deepseek_api import query_deepseek
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pydantic_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def sanitize_function_name(name: str) -> str:
    """Sanitize function names to make them valid PascalCase class names."""
    name = re.sub(r"[^0-9a-zA-Z_]", "", name)
    name_parts = re.split(r'[_\s]+', name)  # Split on underscore or space
    pascal_case = ''.join(word.capitalize() for word in name_parts if word)
    if not pascal_case.isidentifier():
        raise ValueError(f"Invalid function name: {pascal_case}")
    return pascal_case

def map_type(dtype: str) -> str:
    """Normalize types across languages and handle special cases."""
    type_mapping = {
        "HttpRequest": "Any",
        "object": "Dict[str, Any]",
        "array": "List[Any]",
        "string": "str",
        "number": "float",
        "integer": "int",
        "boolean": "bool",
        "void": "None",
        "null": "None",
        None: "Any"
    }
    return type_mapping.get(dtype, dtype)

def extract_models_from_response(response: Dict[str, Any]) -> tuple[Dict[str, str], Dict[str, str]]:
    """Extract and validate models from API response with enhanced checks."""
    try:
        # Handle both direct responses and string responses
        if isinstance(response, str):
            response = json.loads(response.strip("```json\n"))
        
        input_model = response.get("input_model", {})
        output_model = response.get("output_model", {"result": "Any"})
        
        # Validate required fields
        if not isinstance(input_model, dict) or not isinstance(output_model, dict):
            raise ValueError("Invalid model structure")
            
        return input_model, output_model
        
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Response parsing failed: {str(e)}")
        return {}, {"result": "Any"}

def generate_function_code(func_info: Dict[str, Any], input_fields: Dict[str, str], output_fields: Dict[str, str]) -> str:
    """Generate language-specific function implementation with correct parameter names."""
    # Use input field names as function parameters to ensure they match
    param_names = list(input_fields.keys())
    params = ", ".join(param_names)
    docstring = func_info.get("docstring", "").strip()
    
    # Create a default return object with all required fields from the output model
    return_fields = {}
    for field_name, field_type in output_fields.items():
        # Set default values based on type
        if field_type == "str" or "string" in field_type.lower():
            return_fields[field_name] = f'"{field_name} value"'
        elif field_type == "int" or "integer" in field_type.lower():
            return_fields[field_name] = "0"
        elif field_type == "bool" or "boolean" in field_type.lower():
            return_fields[field_name] = "True"
        elif field_type == "float" or "number" in field_type.lower():
            return_fields[field_name] = "0.0"
        elif "list" in field_type.lower() or "array" in field_type.lower():
            return_fields[field_name] = "[]"
        elif "dict" in field_type.lower() or "object" in field_type.lower():
            return_fields[field_name] = "{}"
        else:
            return_fields[field_name] = "None"
    
    # Format the return dictionary
    return_dict = "{\n        " + ",\n        ".join([f'"{k}": {v}' for k, v in return_fields.items()]) + "\n    }"
    
    if func_info.get("language", "python") == "python":
        # Handle the case when there are no parameters
        if not param_names:
            params = "data"
            return f"""def {func_info['name']}(data) -> Dict[str, Any]:
    \"\"\"{docstring}\"\"\"
    # Implementation goes here
    return {return_dict}\n"""
        else:
            return f"""def {func_info['name']}({params}) -> Dict[str, Any]:
    \"\"\"{docstring}\"\"\"
    # Implementation goes here
    return {return_dict}\n"""
    
    elif func_info.get("language") == "javascript":
        return f"""function {func_info['name']}({params}) {{
    /* {docstring} */
    return {return_dict};
}}\n"""
    
    elif func_info.get("language") == "go":
        return f"""func {func_info['name']}({params}) {{
    // {docstring}
    return {return_dict}
}}\n"""
    
    return """# Unsupported language\n"""

def generate_model_class(class_name: str, fields: Dict[str, str], is_input: bool = True) -> str:
    """Generate a complete Pydantic model class with validation."""
    field_lines = []
    for name, dtype in fields.items():
        dtype_normalized = map_type(dtype)
        field_line = f"    {name}: {dtype_normalized}"
        
        # Add field validation for input models
        if is_input:
            if name == "id":
                field_line += " = Field(gt=0)"
            elif name.endswith("_at"):
                field_line += " = Field(default_factory=datetime.now)"
            elif name.endswith("_email"):
                field_line += ' = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")'
        
        field_lines.append(field_line)
    
    return f"class {class_name}(BaseModel):\n" + \
           ("\n".join(field_lines) if field_lines else "    pass") + "\n"

def generate_pydantic_models(parsed_data: Dict[str, Any]) -> Dict[str, str]:
    models = {}
    base_imports = """from pydantic import BaseModel, Field
from typing import Any, Optional, Dict, List, Union
from datetime import datetime
import json\n\n"""

    for file_name, content in parsed_data.items():
        file_context = {
            'imports': set(),
            'custom_types': set()
        }

        for function in content["functions"]:
            try:
                func_info = {
                    "name": function["name"],
                    "parameters": function["parameters"],
                    "return_type": function["return_type"],
                    "docstring": function.get("docstring", ""),
                    "source_code": function.get("source_code", ""),
                    "language": content.get("language", "python")
                }

                # Try to get AI-generated schema
                try:
                    api_response = query_deepseek(func_info)
                    input_model, output_model = extract_models_from_response(api_response)

                    if not input_model:
                        raise ValueError("Empty input model from API")

                except Exception as api_error:
                    logger.warning(f"API failed for {function['name']}: {str(api_error)}")
                    # Fallback to basic types
                    input_model = {p["name"]: map_type(p.get("type")) for p in function["parameters"]}
                    
                    # Improved fallback for output model based on function name
                    if "login" in function["name"].lower():
                        output_model = {
                            "message": "str", 
                            "user_id": "int", 
                            "is_admin": "bool"
                        }
                    elif "user" in function["name"].lower():
                        output_model = {
                            "users": "List[Dict[str, Any]]",
                            "count": "int",
                            "success": "bool"
                        }
                    elif "activa" in function["name"].lower() or "update" in function["name"].lower():
                        output_model = {
                            "success": "bool",
                            "message": "str",
                            "updated_count": "int"
                        }
                    else:
                        output_model = {"result": map_type(function["return_type"])}

                # Generate model code
                safe_name = sanitize_function_name(function["name"])
                pascal_name = "".join(word.capitalize() for word in safe_name.split("_"))
                
                input_model_code = generate_model_class(f"{pascal_name}Input", input_model)
                output_model_code = generate_model_class(f"{pascal_name}Output", output_model, is_input=False)
                function_code = generate_function_code(func_info, input_model, output_model)

                # Combine everything
                model_code = f"""{base_imports}{''.join(file_context['imports'])}

{input_model_code}

{output_model_code}

{function_code}"""

                models[pascal_name] = model_code

            except Exception as e:
                logger.error(f"Failed to generate model for {function.get('name')}: {str(e)}")
                continue

    return models

def dynamic_import_function(module_path: str, function_name: str) -> Optional[Callable]:
    """Dynamically import a function from a Python module."""
    try:
        spec = importlib.util.spec_from_file_location("generated_model", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, function_name, None)
    except Exception as e:
        logger.error(f"Failed to import function {function_name} from {module_path}: {e}")
        return None


def fallback_model_creation(function: Dict[str, Any]) -> tuple:
    """Fallback method to create models when AI API fails."""
    input_model = {param["name"]: map_type(param.get("type")) for param in function["parameters"]}
    
    # More intelligent output model generation based on function name
    if "login" in function["name"].lower():
        output_model = {
            "message": "str", 
            "user_id": "int", 
            "is_admin": "bool"
        }
    elif "user" in function["name"].lower():
        output_model = {
            "users": "List[Dict[str, Any]]",
            "count": "int",
            "success": "bool"
        }
    elif "activa" in function["name"].lower() or "update" in function["name"].lower():
        output_model = {
            "success": "bool",
            "message": "str",
            "updated_count": "int"
        }
    else:
        output_model = {"result": map_type(function.get("return_type"))}
        
    return input_model, output_model

def save_pydantic_models(models: Dict[str, str], output_dir: Path = None) -> None:
    """Save models with better organization and metadata."""
    if not output_dir:
        output_dir = Path(__file__).resolve().parent.parent / "models/generated_models"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for model_name, model_code in models.items():
        file_path = output_dir / f"{model_name}.py"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f'''"""
Auto-generated Pydantic Model for {model_name}
"""
{model_code}''')
            logger.info(f"Saved model to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save {model_name}: {str(e)}")
    
    logger.info(f"All models saved to {output_dir}")