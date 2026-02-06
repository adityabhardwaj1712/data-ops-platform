import sys
import os
import uvicorn

# Simulate uvicorn environment
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_path = os.path.join(project_root, "backend")
sys.path.insert(0, backend_path)

print(f"Path: {sys.path}")

try:
    from app.main import app
    print("✅ Successfully imported app.main:app")
except Exception as e:
    print(f"❌ Failed to import app: {e}")
    # Print full traceback
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Just for fun, if we got here, we could start it, but let's just exit explicitly success
print("Ready to launch.")
