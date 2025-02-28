import pytest
from parser.parser import parse_python_file

def test_function_extraction(tmp_path):
    """Test if the parser extracts functions correctly using a temporary file."""
    sample_code = """
def add(a: int, b: int) -> int:
    \"\"\"Adds two numbers.\"\"\"
    return a + b
"""

    # Create a temporary file
    temp_file = tmp_path / "test_file.py"
    temp_file.write_text(sample_code)

    # Now pass the temp file path to parse_python_file
    parsed_data = parse_python_file(str(temp_file))

    assert len(parsed_data["functions"]) == 1
    assert parsed_data["functions"][0]["name"] == "add"
    assert parsed_data["functions"][0]["parameters"] == ["a", "b"]
    assert parsed_data["functions"][0]["return_type"] == "int"