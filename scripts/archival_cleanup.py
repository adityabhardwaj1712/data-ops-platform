#!/usr/bin/env python3
"""
Archival Cleanup Script - Sprint 19, Task 136

Purpose: Clean up the repository for v1.0 release.
- Removes temporary caches
- Identifies old experiments for archival
- Prepares git tagging command
"""
import os
import shutil
from pathlib import Path

def cleanup():
    base_dir = Path(__file__).parent.parent
    
    # 1. Clean caches
    cache_dirs = [
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "backend/app/__pycache__",
        "backend/app/core/__pycache__",
        "backend/app/api/__pycache__",
        "backend/app/db/__pycache__",
        "backend/app/worker/__pycache__",
        "backend/app/scraper/__pycache__",
    ]
    
    print("🧹 Cleaning caches...")
    for d in cache_dirs:
        dir_path = base_dir / d
        if dir_path.exists():
            print(f"  Removing {d}")
            shutil.rmtree(dir_path)
    
    # 2. Identify and handle 'experiments' if they exist in a known location
    # For this project, let's assume we move any .py files in a potential 'experiments' folder to an archive
    experiments_dir = base_dir / "experiments"
    archive_dir = base_dir / "archive/experiments"
    
    if experiments_dir.exists():
        print(f"📦 Archiving experiments to {archive_dir}...")
        archive_dir.mkdir(parents=True, exist_ok=True)
        for item in experiments_dir.iterdir():
            if item.is_file():
                print(f"  Moving {item.name}")
                shutil.move(str(item), str(archive_dir / item.name))
        # Remove empty experiments dir
        if not any(experiments_dir.iterdir()):
            experiments_dir.rmdir()
    else:
        print("ℹ️ No 'experiments' directory found to archive.")

    # 3. Clean environment files or temporary logs
    temp_files = [".DS_Store", "thumbs.db", "bad_day_results.json"]
    print("🧹 Cleaning temp files...")
    for f in temp_files:
        f_path = base_dir / f
        if f_path.exists():
            print(f"  Removing {f}")
            os.remove(f_path)

    print("\n✅ Cleanup complete.")
    print("\n🚀 FINAL STEPS FOR USER:")
    print("1. Run: git add .")
    print("2. Run: git commit -m \"chore: final cleanup for v1.0 release\"")
    print("3. Run: git tag -a v1.0 -m \"Production-ready release\"")
    print("4. Run: git push origin main --tags")

if __name__ == "__main__":
    cleanup()
