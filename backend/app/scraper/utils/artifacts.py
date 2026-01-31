import os
import uuid
import datetime
from pathlib import Path
from typing import Optional

class ScrapeArtifacts:
    """
    Manages storage for scraping artifacts (HTML dumps, screenshots).
    """
    
    def __init__(self, base_dir: str = "data/artifacts"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_html(self, html: str, job_id: str) -> str:
        """Saves HTML content to a file in a job-specific subfolder."""
        job_dir = self.base_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{datetime.datetime.now().strftime('%H%M%S')}.html"
        file_path = job_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        return str(file_path).replace("\\", "/") # Ensure forward slashes for URLs

    def save_screenshot(self, screenshot_bytes: bytes, job_id: str) -> str:
        """Saves screenshot bytes to a file in a job-specific subfolder."""
        job_dir = self.base_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{datetime.datetime.now().strftime('%H%M%S')}.png"
        file_path = job_dir / filename
        with open(file_path, "wb") as f:
            f.write(screenshot_bytes)
        return str(file_path).replace("\\", "/") # Ensure forward slashes for URLs

    def save_json(self, data: dict, job_id: str) -> str:
        """Saves a dictionary as a JSON file in a job-specific subfolder."""
        import json
        job_dir = self.base_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{datetime.datetime.now().strftime('%H%M%S')}.json"
        file_path = job_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return str(file_path).replace("\\", "/")

    def get_artifacts_for_job(self, job_id: str) -> list:
        """Lists artifacts associated with a job ID."""
        job_dir = self.base_dir / job_id
        if not job_dir.exists():
            return []
        return [str(p).replace("\\", "/") for p in job_dir.glob("*")]
