import sys
import os

# Set up path as uvicorn would
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_path = os.path.join(project_root, "backend")
sys.path.insert(0, backend_path)

print(f"Path: {sys.path}")

try:
    print("Attempting to import app.schemas...")
    import app.schemas
    print("✅ app.schemas imported")
except Exception as e:
    print(f"❌ Failed to import app.schemas: {e}")

try:
    print("Attempting to import app.api.hitl...")
    import app.api.hitl
    print("✅ app.api.hitl imported")
except Exception as e:
    print(f"❌ Failed to import app.api.hitl: {e}")
