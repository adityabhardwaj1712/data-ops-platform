"""
2️⃣ SOURCE HEALTH TRACKING
Tracks domain health to learn which sites are reliable

Your system learns:
"This site is bad → don't hit too often"

This is how pro crawlers behave.
"""
from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base
import uuid


class SourceHealth(Base):
    """
    Tracks health metrics for scraping sources.
    
    Used to:
    - Avoid hitting unreliable sources too often
    - Prioritize high-success-rate domains
    - Auto-block problematic sources
    """
    __tablename__ = "source_health"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    
    # Statistics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    success_rate = Column(Float, default=1.0)
    
    # Rolling averages
    avg_response_time_ms = Column(Float, nullable=True)
    avg_content_size = Column(Integer, nullable=True)
    
    # Status
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(String(255), nullable=True)
    consecutive_failures = Column(Integer, default=0)
    
    # Timestamps
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_checked = Column(DateTime(timezone=True), onupdate=func.now())
    last_success = Column(DateTime(timezone=True), nullable=True)
    last_failure = Column(DateTime(timezone=True), nullable=True)
    
    # Strategy hints (learned from experience)
    requires_browser = Column(Boolean, default=False)
    requires_stealth = Column(Boolean, default=False)
    has_rate_limit = Column(Boolean, default=False)
    
    def update_stats(self, success: bool, response_time_ms: float = None, content_size: int = None):
        """Update stats after a request"""
        from datetime import datetime
        
        self.total_requests += 1
        
        if success:
            self.successful_requests += 1
            self.consecutive_failures = 0
            self.last_success = datetime.now()
        else:
            self.failed_requests += 1
            self.consecutive_failures += 1
            self.last_failure = datetime.now()
        
        # Recalculate success rate
        self.success_rate = self.successful_requests / max(self.total_requests, 1)
        
        # Update rolling averages
        if response_time_ms is not None:
            if self.avg_response_time_ms is None:
                self.avg_response_time_ms = response_time_ms
            else:
                # Exponential moving average
                self.avg_response_time_ms = 0.9 * self.avg_response_time_ms + 0.1 * response_time_ms
        
        if content_size is not None:
            if self.avg_content_size is None:
                self.avg_content_size = content_size
            else:
                self.avg_content_size = int(0.9 * self.avg_content_size + 0.1 * content_size)
        
        # Auto-block if too many failures
        if self.consecutive_failures >= 5:
            self.is_blocked = True
            self.block_reason = "Too many consecutive failures"
    
    @property
    def health_score(self) -> float:
        """
        Calculate overall health score (0-1).
        Higher is better.
        """
        score = self.success_rate
        
        # Penalize blocked domains
        if self.is_blocked:
            return 0.0
        
        # Bonus for many successful requests
        if self.successful_requests > 100:
            score *= 1.1
        
        # Penalize slow responses
        if self.avg_response_time_ms and self.avg_response_time_ms > 5000:
            score *= 0.9
        
        return min(score, 1.0)
