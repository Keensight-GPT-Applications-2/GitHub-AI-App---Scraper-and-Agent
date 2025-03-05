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
    """Extract return type from AST node, handling generics."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Subscript):  # Handle generics like List[str]
        return f"{node.value.id}[{node.slice.id}]"
    else:
        return "Optional[Any]"

def is_public_function(function_name):
    """Check if a function is public (not private or internal)."""
    return not function_name.startswith("_")

def parse_python_file(file_path):
    """Parse a Python file and extract functions, classes, and docstrings."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()

        tree = ast.parse(source_code)
        functions = []
        classes = []

        for node in ast.walk(tree):
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
                classes.append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node) or "No docstring provided.",
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef) and is_public_function(n.name)]
                })

        return {"functions": functions, "classes": classes}

    except SyntaxError as e:
        print(f"❌ SyntaxError in file {file_path}: {e}")
        return {"functions": [], "classes": []}

def parse_javascript_file(file_path):
    """Parse a JavaScript file using Esprima and extract functions."""
    try:
        result = subprocess.run(["node", "parse_js.js", file_path], capture_output=True, text=True)
        return json.loads(result.stdout) if result.stdout else {"functions": [], "classes": []}
    except Exception as e:
        print(f"❌ Error parsing JavaScript file {file_path}: {e}")
        return {"functions": [], "classes": []}

def parse_go_file(file_path):
    """Parse a Go file using a Go parser script and extract functions."""
    try:
        result = subprocess.run(["go", "run", "parse_go.go", file_path], capture_output=True, text=True)
        return json.loads(result.stdout) if result.stdout else {"functions": [], "classes": []}
    except Exception as e:
        print(f"❌ Error parsing Go file {file_path}: {e}")
        return {"functions": [], "classes": []}

def parse_directory(directory_path):
    """Parse all Python, JavaScript, and Go files in a directory."""
    directory_path = Path(directory_path)
    if not directory_path.exists():
        print(f"❌ Error: Directory '{directory_path}' does not exist.")
        return {}

    results = {}
    
    for file_path in directory_path.rglob("*"):
        if file_path.suffix == ".py":
            print(f"📂 Parsing Python file: {file_path}...")
            results[file_path.name] = parse_python_file(file_path)
        elif file_path.suffix == ".js":
            print(f"📂 Parsing JavaScript file: {file_path}...")
            results[file_path.name] = parse_javascript_file(file_path)
        elif file_path.suffix == ".go":
            print(f"📂 Parsing Go file: {file_path}...")
            results[file_path.name] = parse_go_file(file_path)
    
    return results

def get_latest_scraped_repo(base_dir):
    """Find the most recently modified repository in the scraped_repos folder."""
    base_dir = Path(base_dir)
    if not base_dir.exists():
        print(f"❌ Error: Base directory '{base_dir}' does not exist.")
        return None
    latest_repo = max(base_dir.glob("*/"), key=os.path.getmtime, default=None)
    return latest_repo

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
