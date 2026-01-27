import sys
import os

# Add the current directory to sys.path so we can import app
sys.path.append(os.getcwd())

print("Attempting to import app.main...")
try:
    from app.main import app
    print("SUCCESS: app.main imported successfully.")
except ImportError as e:
    print(f"FAILURE: ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAILURE: Exception during import: {e}")
    sys.exit(1)
