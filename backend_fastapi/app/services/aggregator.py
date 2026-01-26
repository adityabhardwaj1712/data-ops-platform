"""
6️⃣ RESULT AGGREGATOR
Collects all successful task results and builds final datasets

Instead of saving: [{job}]
You save: [{job1}, {job2}, {job3}, ...]

This turns tasks → real datasets.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime
import json
import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Job, Task, DatasetVersion, TaskStatus, TaskType
from app.services.normalizer import normalizer
from app.services.deduplicator import deduplicator


@dataclass
class AggregationResult:
    """Result of aggregating task results"""
    success: bool
    total_items: int
    unique_items: int
    duplicates_removed: int
    data: List[Dict[str, Any]]
    version_created: Optional[int] = None
    file_path: Optional[str] = None
    errors: List[str] = field(default_factory=list)


class ResultAggregator:
    """
    Aggregates results from all completed tasks into a final dataset.
    
    Responsibilities:
    - Collect all successful task results
    - Normalize data
    - Deduplicate
    - Create versioned dataset
    """
    
    async def aggregate_job_results(
        self,
        job_id: UUID,
        db: AsyncSession,
        normalize: bool = True,
        deduplicate: bool = True,
        key_fields: List[str] = None
    ) -> AggregationResult:
        """
        Aggregate all completed task results for a job.
        
        Args:
            job_id: Job UUID
            db: Database session
            normalize: Whether to normalize data
            deduplicate: Whether to deduplicate
            key_fields: Fields for deduplication
            
        Returns:
            AggregationResult with final dataset
        """
        # Get job
        job_result = await db.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        
        if not job:
            return AggregationResult(
                success=False,
                total_items=0,
                unique_items=0,
                duplicates_removed=0,
                data=[],
                errors=["Job not found"]
            )
        
        # Get all completed tasks with results
        tasks_result = await db.execute(
            select(Task)
            .where(Task.job_id == job_id)
            .where(Task.status == TaskStatus.COMPLETED)
            .where(Task.result.isnot(None))
        )
        tasks = tasks_result.scalars().all()
        
        # Collect all results
        all_items = []
        for task in tasks:
            if isinstance(task.result, dict):
                # Single item
                item = task.result.copy()
                item['_task_id'] = str(task.id)
                item['_confidence'] = task.confidence or 0.0
                all_items.append(item)
            elif isinstance(task.result, list):
                # Multiple items
                for item in task.result:
                    if isinstance(item, dict):
                        item['_task_id'] = str(task.id)
                        item['_confidence'] = task.confidence or 0.0
                        all_items.append(item)
        
        if not all_items:
            return AggregationResult(
                success=False,
                total_items=0,
                unique_items=0,
                duplicates_removed=0,
                data=[],
                errors=["No completed tasks with results"]
            )
        
        total_items = len(all_items)
        
        # Normalize
        if normalize:
            all_items = normalizer.normalize_batch(all_items)
        
        # Deduplicate
        duplicates_removed = 0
        if deduplicate:
            dedupe_result = deduplicator.deduplicate(
                all_items,
                key_fields=key_fields,
                keep="highest_confidence"
            )
            all_items = dedupe_result.unique_items
            duplicates_removed = dedupe_result.duplicates_removed
        
        return AggregationResult(
            success=True,
            total_items=total_items,
            unique_items=len(all_items),
            duplicates_removed=duplicates_removed,
            data=all_items
        )
    
    async def create_dataset_version(
        self,
        job_id: UUID,
        db: AsyncSession,
        normalize: bool = True,
        deduplicate: bool = True,
        key_fields: List[str] = None
    ) -> AggregationResult:
        """
        Aggregate results and create a new dataset version.
        """
        # Aggregate
        result = await self.aggregate_job_results(
            job_id, db, normalize, deduplicate, key_fields
        )
        
        if not result.success:
            return result
        
        # Get latest version number
        job_result = await db.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        
        versions_result = await db.execute(
            select(DatasetVersion)
            .where(DatasetVersion.job_id == job_id)
            .order_by(DatasetVersion.version.desc())
        )
        versions = versions_result.scalars().all()
        latest_version = versions[0].version if versions else 0
        new_version = latest_version + 1
        
        # Save to file
        base_path = os.path.join(os.getcwd(), "data", "versions")
        os.makedirs(base_path, exist_ok=True)
        
        file_path = os.path.join(base_path, f"job_{job_id}_v{new_version}.json")
        
        # Clean metadata from saved data
        clean_data = []
        for item in result.data:
            clean_item = {k: v for k, v in item.items() if not k.startswith('_')}
            clean_data.append(clean_item)
        
        with open(file_path, "w") as f:
            json.dump(clean_data, f, indent=2, default=str)
        
        # Calculate confidence summary
        confidences = [item.get('_confidence', 0) for item in result.data]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Create version record
        dataset_version = DatasetVersion(
            job_id=job_id,
            version=new_version,
            data_location=file_path,
            row_count=len(clean_data),
            confidence_summary={
                "avg_confidence": round(avg_confidence, 2),
                "min_confidence": round(min(confidences), 2) if confidences else 0,
                "max_confidence": round(max(confidences), 2) if confidences else 0,
                "total_items": result.total_items,
                "unique_items": result.unique_items,
                "duplicates_removed": result.duplicates_removed
            }
        )
        db.add(dataset_version)
        await db.commit()
        
        result.version_created = new_version
        result.file_path = file_path
        
        return result


# Global instance
aggregator = ResultAggregator()
