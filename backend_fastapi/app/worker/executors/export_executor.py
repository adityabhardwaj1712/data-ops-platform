"""
Export Job Executor
Lazy-loads heavy export dependencies (Pandas, openpyxl) only when needed
"""

import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ExportExecutor:
    """
    Executes export jobs with lazy-loaded dependencies.
    
    Heavy libraries (Pandas, openpyxl) are imported only when this executor is first used.
    """
    
    def __init__(self):
        self._exporter = None
    
    def _load_exporter(self):
        """Lazy-load the exporter service (HEAVY)."""
        if self._exporter is None:
            logger.info("Loading exporter service (heavy dependencies: pandas, openpyxl)...")
            
            # Import heavy libraries only when needed
            from app.services.exporter import ExportService
            self._exporter = ExportService()
            
            logger.info("Exporter service loaded successfully")
    
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an export job.
        
        Args:
            payload: Job payload containing:
                - job_id: Job ID to export
                - version: Dataset version (optional)
                - format: Export format (excel/csv/json)
                - include_source_links: Include source URLs
                - include_confidence: Include confidence scores
        
        Returns:
            Export result with file path and metadata
        """
        # Lazy-load exporter on first use
        self._load_exporter()
        
        # Extract parameters from payload
        job_id = payload.get("job_id")
        version = payload.get("version")
        export_format = payload.get("format", "excel")
        include_source_links = payload.get("include_source_links", True)
        include_confidence = payload.get("include_confidence", True)
        
        logger.info(f"Executing export job for job_id={job_id}, format={export_format}")
        
        # Execute export
        result = await self._exporter.export_job(
            job_id=job_id,
            version=version,
            format=export_format,
            include_source_links=include_source_links,
            include_confidence=include_confidence
        )
        
        # Convert result to dict
        result_dict = {
            "success": True,
            "file_path": str(result.get("file_path", "")),
            "file_url": result.get("file_url", ""),
            "row_count": result.get("row_count", 0),
            "format": export_format,
            "job_id": str(job_id),
            "version": version
        }
        
        logger.info(f"Export job completed: {result_dict['row_count']} rows exported")
        
        return result_dict
