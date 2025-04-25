import sys
from pathlib import Path

# Add models/generated_models to sys.path
sys.path.insert(0, str(Path(__file__).parent / "models" / "generated_models"))

try:
    from Adminactivausers import AdminActivaUsers
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

def test_func():
    try:
        result = AdminActivaUsers({"user_ids": [1, 2, 3], "is_active": True})
        print("Function call result:", result)
    except Exception as e:
        print(f"Function call failed: {e}")

if __name__ == "__main__":
    test_func()
