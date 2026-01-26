"""
Backup & Restore Service
Create backups of datasets and restore them
"""
import json
import os
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Job, DatasetVersion
from app.core.config import settings

logger = logging.getLogger(__name__)


class BackupService:
    """Service for backing up and restoring data"""
    
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    async def create_backup(
        self,
        db: AsyncSession,
        job_id: UUID,
        include_data: bool = True
    ) -> Dict[str, Any]:
        """Create a backup of a job and its datasets"""
        # Get job
        stmt = select(Job).where(Job.id == job_id)
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Get all dataset versions
        stmt = select(DatasetVersion).where(DatasetVersion.job_id == job_id)
        result = await db.execute(stmt)
        versions = result.scalars().all()
        
        backup_data = {
            "job": {
                "id": str(job.id),
                "name": job.name,
                "intent": job.intent,
                "description": job.description,
                "status": job.status.value,
                "created_at": job.created_at.isoformat()
            },
            "versions": [],
            "backup_created_at": datetime.utcnow().isoformat()
        }
        
        # Backup dataset files
        for version in versions:
            version_data = {
                "version": version.version,
                "row_count": version.row_count,
                "created_at": version.created_at.isoformat()
            }
            
            if include_data and version.data_location and os.path.exists(version.data_location):
                # Copy data file to backup
                backup_file = self.backup_dir / f"{job_id}_{version.version}.json"
                shutil.copy2(version.data_location, backup_file)
                version_data["data_file"] = str(backup_file)
            
            backup_data["versions"].append(version_data)
        
        # Save backup metadata
        backup_file = self.backup_dir / f"backup_{job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2)
        
        logger.info(f"Created backup for job {job_id}: {backup_file}")
        
        return {
            "backup_file": str(backup_file),
            "job_id": str(job_id),
            "versions_backed_up": len(backup_data["versions"]),
            "created_at": backup_data["backup_created_at"]
        }
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("backup_*.json"):
            try:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                backups.append({
                    "file": str(backup_file),
                    "job_id": backup_data["job"]["id"],
                    "job_name": backup_data["job"]["name"],
                    "versions": len(backup_data["versions"]),
                    "created_at": backup_data["backup_created_at"]
                })
            except Exception as e:
                logger.error(f"Error reading backup {backup_file}: {e}")
        
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)
    
    async def restore_backup(
        self,
        db: AsyncSession,
        backup_file: str
    ) -> Dict[str, Any]:
        """Restore a backup (creates new job with same data)"""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            raise ValueError(f"Backup file not found: {backup_file}")
        
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Create new job
        new_job = Job(
            name=f"{backup_data['job']['name']} (Restored)",
            intent=backup_data['job']['intent'],
            description=backup_data['job']['description'],
            status="PENDING"
        )
        
        db.add(new_job)
        await db.flush()
        
        # Restore dataset versions
        restored_versions = []
        for version_data in backup_data['versions']:
            if 'data_file' in version_data and os.path.exists(version_data['data_file']):
                # Copy data file to data directory
                data_dir = Path("data/versions")
                data_dir.mkdir(parents=True, exist_ok=True)
                
                new_data_file = data_dir / f"{new_job.id}_{version_data['version']}.json"
                shutil.copy2(version_data['data_file'], new_data_file)
                
                new_version = DatasetVersion(
                    job_id=new_job.id,
                    version=version_data['version'],
                    data_location=str(new_data_file),
                    row_count=version_data['row_count']
                )
                
                db.add(new_version)
                restored_versions.append(version_data['version'])
        
        await db.commit()
        
        logger.info(f"Restored backup {backup_file} as job {new_job.id}")
        
        return {
            "job_id": str(new_job.id),
            "restored_versions": restored_versions,
            "restored_at": datetime.utcnow().isoformat()
        }


# Global instance
backup_service = BackupService()
