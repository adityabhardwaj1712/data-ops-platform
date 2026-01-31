import logging
from typing import Optional
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import DomainMemory
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class DomainMemoryManager:
    """
    Handles persistence of domain-specific scraping intelligence.
    """
    
    @staticmethod
    async def get_best_strategy(db: AsyncSession, url: str) -> Optional[str]:
        domain = urlparse(url).netloc
        try:
            result = await db.execute(select(DomainMemory).where(DomainMemory.domain == domain))
            memory = result.scalar_one_or_none()
            if memory and memory.success_rate > 0.7:
                return memory.best_strategy
        except Exception as e:
            logger.error(f"Failed to fetch domain memory: {e}")
        return None

    @staticmethod
    async def record_result(db: AsyncSession, url: str, strategy: str, success: bool, latency: float):
        domain = urlparse(url).netloc
        try:
            result = await db.execute(select(DomainMemory).where(DomainMemory.domain == domain))
            memory = result.scalar_one_or_none()
            
            if memory:
                # Update existing memory with rolling average
                new_count = memory.job_count + 1
                new_success_rate = (memory.success_rate * memory.job_count + (1 if success else 0)) / new_count
                new_latency = (memory.avg_latency * memory.job_count + latency) / new_count
                
                # Simple logic: if new strategy works and old one had lower success, update it
                # For now, we just update the stats
                await db.execute(
                    update(DomainMemory)
                    .where(DomainMemory.domain == domain)
                    .values(
                        success_rate=new_success_rate,
                        avg_latency=new_latency,
                        job_count=new_count,
                        best_strategy=strategy if success and new_success_rate >= memory.success_rate else memory.best_strategy
                    )
                )
            else:
                # Create new entry
                await db.execute(
                    insert(DomainMemory).values(
                        domain=domain,
                        best_strategy=strategy,
                        success_rate=1.0 if success else 0.0,
                        avg_latency=latency,
                        job_count=1
                    )
                )
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to record domain memory: {e}")
            await db.rollback()
