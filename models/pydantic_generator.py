import re
from pydantic import BaseModel
from typing import Any
from pathlib import Path


def sanitize_function_name(name):
    """Sanitize function names to make them valid Python identifiers."""
    name = name.replace("__", "").capitalize()
    name = re.sub(r"[^0-9a-zA-Z_]", "", name)
    if not name.isidentifier():
        raise ValueError(f"Invalid function name: {name}")
    return name


def generate_pydantic_models(parsed_data):
    """
    Generate Pydantic input/output models for parsed functions.
    """
    models = []

    # Add necessary imports for each file
    imports = (
        "from pydantic import BaseModel\n"
        "from typing import Any, Optional\n\n"
    )

    for file_name, content in parsed_data.items():
        for function in content["functions"]:
            # Sanitize function name
            safe_function_name = sanitize_function_name(function["name"])

            # Input Model
            input_model_name = f"{safe_function_name}Input"
            input_model_fields = "\n".join(
                [f"    {param}: Any  # Default type is 'Any'" for param in function["parameters"]]
            )

            # Output Model
            output_model_name = f"{safe_function_name}Output"
            output_model_field = (
                f"    result: {function['return_type'] or 'Optional[Any]'} = None  # Return type inferred or defaulted"
            )

            # Combine Models
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
    """
    Save Pydantic models to .py files.
    """
    # Set the correct output directory relative to the project root
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent / "models/generated_models"
    else:
        output_dir = Path(output_dir).resolve()

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save each model in a separate file
    for idx, model_code in enumerate(models, start=1):
        file_path = output_path / f"model_{idx}.py"

        # Add a header comment to the model file
        file_header = f'''"""
Auto-generated Pydantic Models
File: {file_path.name}
"""
'''
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_header + model_code.strip())
        print(f"Model saved to {file_path}")
