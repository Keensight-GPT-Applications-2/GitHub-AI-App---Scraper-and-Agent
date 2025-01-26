import os
import ast
import sys
from pathlib import Path


project_root = Path(__file__).resolve().parent.parent  # Adjust path to point to the root folder
sys.path.append(str(project_root))

from models.pydantic_generator import generate_pydantic_models, save_pydantic_models

def parse_python_file(file_path):
    """Parse a Python file and extract functions, classes, and docstrings."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()

        # Parse the file using AST
        tree = ast.parse(source_code)

        functions = []
        classes = []

        # Walk through the AST nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "parameters": [arg.arg for arg in node.args.args],
                    "return_type": getattr(node.returns, 'id', None) if node.returns else None
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                })

        return {"functions": functions, "classes": classes}

    except SyntaxError as e:
        print(f"SyntaxError in file {file_path}: {e}")
        return {"functions": [], "classes": []}


def parse_directory(directory_path):
    """Parse all Python files in a directory."""
    directory_path = Path(directory_path)
    if not directory_path.exists():
        print(f"Error: Directory '{directory_path}' does not exist.")
        return

    results = {}

    # Traverse all Python files recursively
    for file_path in directory_path.rglob("*.py"):
        print(f"Parsing {file_path}...")
        results[file_path.name] = parse_python_file(file_path)

    return results


def get_latest_scraped_repo(base_dir):
    """Find the most recently modified repository in the scraped_repos folder."""
    base_dir = Path(base_dir)
    if not base_dir.exists():
        print(f"Error: Base directory '{base_dir}' does not exist.")
        return None

    # Find the most recently modified folder in the base directory
    latest_repo = max(base_dir.glob("*/"), key=os.path.getmtime, default=None)
    return latest_repo


if __name__ == "__main__":
    # Automatically locate the latest scraped repository
    base_scraped_dir = "../scraper/scraped_repos"
    latest_repo_dir = get_latest_scraped_repo(base_scraped_dir)

    if latest_repo_dir:
        print(f"Parsing the latest repository: {latest_repo_dir}")
        parsed_results = parse_directory(latest_repo_dir)

        # Display the extracted information
        if parsed_results:
            for file_name, content in parsed_results.items():
                print(f"\nFile: {file_name}")
                if content["functions"] or content["classes"]:
                    print("Functions:")
                    for func in content["functions"]:
                        print(f"  - Name: {func['name']}")
                        print(f"    Docstring: {func['docstring']}")
                        print(f"    Parameters: {func['parameters']}")
                        print(f"    Return Type: {func['return_type']}")
                    print("Classes:")
                    for cls in content["classes"]:
                        print(f"  - Name: {cls['name']}")
                        print(f"    Docstring: {cls['docstring']}")
                        print(f"    Methods: {cls['methods']}")
                else:
                    print("No functions or classes found in this file.")

            # Generate Pydantic Models
            print("\nGenerating Pydantic models...")
            models = generate_pydantic_models(parsed_results)

            # Save the models to files
            print("\nSaving Pydantic models...")
            save_pydantic_models(models)

    else:
        print("No scraped repositories found.")
