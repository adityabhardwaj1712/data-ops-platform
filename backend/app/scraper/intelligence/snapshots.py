import logging
import json
import hashlib
from typing import Dict, Any, Optional
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import DataSnapshot

logger = logging.getLogger(__name__)

class SnapshotManager:
    """
    Handles data snapshots for change detection.
    """
    
    @staticmethod
    async def save_snapshot(db: AsyncSession, job_id: str, url: str, data: Dict[str, Any]):
        try:
            # Create a string representation for hashing
            data_str = json.dumps(data, sort_keys=True)
            data_hash = hashlib.sha256(data_str.encode()).hexdigest()
            
            # Store snapshot
            await db.execute(
                insert(DataSnapshot).values(
                    job_id=job_id,
                    url=url,
                    data_hash=data_hash,
                    data_json=data,
                )
            )
            await db.commit()
            logger.info(f"Saved data snapshot for {url} (Hash: {data_hash[:8]})")
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            await db.rollback()

    @staticmethod
    async def get_last_snapshot(db: AsyncSession, url: str) -> Optional[DataSnapshot]:
        try:
            result = await db.execute(
                select(DataSnapshot)
                .where(DataSnapshot.url == url)
                .order_by(DataSnapshot.timestamp.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to fetch last snapshot: {e}")
            return None
