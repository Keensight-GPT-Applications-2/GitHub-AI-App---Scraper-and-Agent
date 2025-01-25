from pydantic import BaseModel
from typing import Any
from pathlib import Path


def generate_pydantic_models(parsed_data):
    """
    Generate Pydantic input/output models for parsed functions.
    """
    models = []

    for file_name, content in parsed_data.items():
        for function in content["functions"]:
            # Input Model
            input_model_name = f"{function['name'].capitalize()}Input"
            input_model_fields = "\n".join(
                [f"    {param}: Any  # Default type is 'Any'" for param in function["parameters"]]
            )

            # Output Model
            output_model_name = f"{function['name'].capitalize()}Output"
            output_model_field = f"    result: {function['return_type'] or 'Any'}  # Return type inferred"

            # Combine Models
            model_code = f"""
class {input_model_name}(BaseModel):
{input_model_fields if input_model_fields else '    pass'}

class {output_model_name}(BaseModel):
{output_model_field}
"""
            models.append(model_code)

    return models


def save_pydantic_models(models, output_dir="models/generated_models"):
    """
    Save Pydantic models to .py files.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save each model in a separate file
    for idx, model_code in enumerate(models, start=1):
        file_path = output_path / f"model_{idx}.py"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"from pydantic import BaseModel\nfrom typing import Any\n\n{model_code.strip()}")
        print(f"Model saved to {file_path}")
