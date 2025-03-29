import os
import ast
import sys
import subprocess
import json
from pathlib import Path

# Ensure correct imports from updated generator
project_root = Path(__file__).resolve().parent.parent  
sys.path.append(str(project_root))

from models.pydantic_generator import generate_pydantic_models, save_pydantic_models

def extract_return_type(node):
    """Extract return type from AST node, handling generics and edge cases."""
    try:
        if isinstance(node, ast.Name):
            return node.id  # e.g., str, int
        elif isinstance(node, ast.Subscript):  # e.g., List[str]
            value_id = node.value.id if isinstance(node.value, ast.Name) else "Any"
            # Different AST versions (Python 3.8+)
            if hasattr(node.slice, 'id'):
                slice_id = node.slice.id
            elif hasattr(node.slice, 'value'):
                slice_id = node.slice.value if isinstance(node.slice.value, str) else "Any"
            else:
                slice_id = "Any"
            return f"{value_id}[{slice_id}]"
        elif isinstance(node, ast.Attribute):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return type(node.value).__name__
        else:
            return "Optional[Any]"
    except Exception as e:
        print(f"⚠️ Failed to extract return type: {e}")
        return "Optional[Any]"

def is_public_function(function_name):
    return not function_name.startswith("_")

def parse_python_file(file_path):
    """Parse a Python file and extract functions, classes, and docstrings."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()

        tree = ast.parse(source_code, filename=str(file_path))
        functions = []
        classes = []

        for node in ast.iter_child_nodes(tree):  # More efficient than ast.walk
            try:
                if isinstance(node, ast.FunctionDef) and is_public_function(node.name):
                    params = [arg.arg for arg in node.args.args if arg.arg != "self"]
                    return_type = extract_return_type(node.returns) if node.returns else "Optional[Any]"
                    functions.append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node) or "No docstring provided.",
                        "parameters": params,
                        "return_type": return_type
                    })

                elif isinstance(node, ast.ClassDef):
                    class_methods = []
                    for sub_node in node.body:
                        if isinstance(sub_node, ast.FunctionDef) and is_public_function(sub_node.name):
                            class_methods.append(sub_node.name)
                    classes.append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node) or "No docstring provided.",
                        "methods": class_methods
                    })
            except Exception as inner_e:
                print(f"⚠️ Skipping node due to error: {inner_e}")

        return {"functions": functions, "classes": classes}

    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"❌ Failed to parse {file_path}: {e}")
        return {"functions": [], "classes": []}

def parse_javascript_file(file_path):
    try:
        result = subprocess.run(["node", "parse_js.js", file_path], capture_output=True, text=True)
        return json.loads(result.stdout) if result.stdout else {"functions": [], "classes": []}
    except Exception as e:
        print(f"❌ Error parsing JavaScript file {file_path}: {e}")
        return {"functions": [], "classes": []}

def parse_go_file(file_path):
    try:
        result = subprocess.run(["go", "run", "parse_go.go", file_path], capture_output=True, text=True)
        return json.loads(result.stdout) if result.stdout else {"functions": [], "classes": []}
    except Exception as e:
        print(f"❌ Error parsing Go file {file_path}: {e}")
        return {"functions": [], "classes": []}

def parse_directory(directory_path):
    directory_path = Path(directory_path)
    if not directory_path.exists():
        print(f"❌ Error: Directory '{directory_path}' does not exist.")
        return {}

    results = {}

    for file_path in directory_path.rglob("*"):
        try:
            if file_path.suffix == ".py":
                print(f"📂 Parsing Python file: {file_path}...")
                results[file_path.name] = parse_python_file(file_path)
            elif file_path.suffix == ".js":
                print(f"📂 Parsing JavaScript file: {file_path}...")
                results[file_path.name] = parse_javascript_file(file_path)
            elif file_path.suffix == ".go":
                print(f"📂 Parsing Go file: {file_path}...")
                results[file_path.name] = parse_go_file(file_path)
        except Exception as file_err:
            print(f"❌ Error processing {file_path}: {file_err}")
    
    return results

def get_latest_scraped_repo(base_dir):
    base_dir = Path(base_dir)
    if not base_dir.exists():
        print(f"❌ Error: Base directory '{base_dir}' does not exist.")
        return None
    return max(base_dir.glob("*/"), key=os.path.getmtime, default=None)

if __name__ == "__main__":
    base_scraped_dir = "../scraper/scraped_repos"
    latest_repo_dir = get_latest_scraped_repo(base_scraped_dir)

    if latest_repo_dir:
        print(f"🚀 Parsing the latest repository: {latest_repo_dir}")
        parsed_results = parse_directory(latest_repo_dir)

        if parsed_results:
            print("\n🚀 Generating Pydantic models...")
            models = generate_pydantic_models(parsed_results)
            print("\n💾 Saving Pydantic models...")
            save_pydantic_models(models)
    else:
        print("❌ No scraped repositories found.")
