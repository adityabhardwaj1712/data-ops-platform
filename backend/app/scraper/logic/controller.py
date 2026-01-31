"""
1️⃣ SCRAPE CONTROLLER
Orchestrates all scraping with limits, backoff, and protection

Prevents:
- IP bans
- CPU spikes
- Container crashes
"""
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from urllib.parse import urlparse
import random
from app.scraper.logic.generic import GenericScraper


@dataclass
class ScrapeStats:
    """Statistics for a domain"""
    domain: str
    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    last_request: Optional[datetime] = None
    consecutive_failures: int = 0
    is_blocked: bool = False
    backoff_until: Optional[datetime] = None


class ScrapeController:
    """
    Controls all scraping operations with:
    - Concurrency limits (max N scrapes at a time)
    - Rate limiting per domain
    - Exponential backoff on failures
    - Domain blacklisting
    
    This is CRITICAL for production use.
    """
    
    def __init__(
        self,
        max_concurrent: int = 5,
        requests_per_domain_per_minute: int = 10,
        max_retries: int = 3,
        base_backoff_seconds: float = 2.0,
        max_backoff_seconds: float = 300.0,  # 5 minutes
        failure_threshold: int = 5  # Block after N consecutive failures
    ):
        self.max_concurrent = max_concurrent
        self.requests_per_domain_per_minute = requests_per_domain_per_minute
        self.max_retries = max_retries
        self.base_backoff = base_backoff_seconds
        self.max_backoff = max_backoff_seconds
        self.failure_threshold = failure_threshold
        
        # Concurrency control
        self._semaphore = asyncio.Semaphore(max_concurrent)
        
        # Domain tracking
        self._domain_stats: Dict[str, ScrapeStats] = {}
        self._domain_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self._domain_request_times: Dict[str, List[datetime]] = defaultdict(list)
        
        # Blacklist
        self._blacklisted_domains: set = set()
    
    async def execute(
        self,
        url: str,
        scrape_fn: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a scrape with all protections.
        
        Args:
            url: URL to scrape
            scrape_fn: Async function to call
            *args, **kwargs: Arguments for scrape_fn
            
        Returns:
            Result from scrape_fn
            
        Raises:
            Exception if domain is blocked or max retries exceeded
        """
        domain = self._get_domain(url)
        
        # Check if domain is blocked
        if self._is_blocked(domain):
            raise Exception(f"Domain {domain} is temporarily blocked")
        
        # Wait for rate limit
        await self._wait_for_rate_limit(domain)
        
        # Acquire semaphore for concurrency control
        async with self._semaphore:
            return await self._execute_with_retry(
                domain, url, scrape_fn, *args, **kwargs
            )
    
    async def _execute_with_retry(
        self,
        domain: str,
        url: str,
        scrape_fn: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute with exponential backoff retry"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                # Record request
                self._record_request(domain)
                
                # Execute scrape
                result = await scrape_fn(url, *args, **kwargs)
                
                # Record success
                self._record_success(domain)
                
                return result
                
            except Exception as e:
                last_exception = e
                self._record_failure(domain)
                
                # Calculate backoff
                backoff = self._calculate_backoff(attempt)
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(backoff)
        
        raise last_exception
    
    async def _wait_for_rate_limit(self, domain: str):
        """Wait if rate limit exceeded for domain"""
        async with self._domain_locks[domain]:
            now = datetime.now()
            
            # Check backoff
            stats = self._domain_stats.get(domain)
            if stats and stats.backoff_until and now < stats.backoff_until:
                wait_time = (stats.backoff_until - now).total_seconds()
                await asyncio.sleep(wait_time)
            
            # Clean old request times (older than 1 minute)
            cutoff = now - timedelta(minutes=1)
            self._domain_request_times[domain] = [
                t for t in self._domain_request_times[domain]
                if t > cutoff
            ]
            
            # Check rate limit
            if len(self._domain_request_times[domain]) >= self.requests_per_domain_per_minute:
                # Wait until oldest request expires
                oldest = min(self._domain_request_times[domain])
                wait_time = (oldest + timedelta(minutes=1) - now).total_seconds()
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
    
    def _record_request(self, domain: str):
        """Record a request to a domain"""
        now = datetime.now()
        self._domain_request_times[domain].append(now)
        
        if domain not in self._domain_stats:
            self._domain_stats[domain] = ScrapeStats(domain=domain)
        
        self._domain_stats[domain].total_requests += 1
        self._domain_stats[domain].last_request = now
    
    def _record_success(self, domain: str):
        """Record successful request"""
        if domain in self._domain_stats:
            self._domain_stats[domain].successful += 1
            self._domain_stats[domain].consecutive_failures = 0
            self._domain_stats[domain].is_blocked = False
            self._domain_stats[domain].backoff_until = None
    
    def _record_failure(self, domain: str):
        """Record failed request"""
        if domain in self._domain_stats:
            stats = self._domain_stats[domain]
            stats.failed += 1
            stats.consecutive_failures += 1
            
            # Apply backoff
            backoff = self._calculate_backoff(stats.consecutive_failures)
            stats.backoff_until = datetime.now() + timedelta(seconds=backoff)
            
            # Block if too many failures
            if stats.consecutive_failures >= self.failure_threshold:
                stats.is_blocked = True
                self._blacklisted_domains.add(domain)
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff with jitter"""
        backoff = self.base_backoff * (2 ** attempt)
        backoff = min(backoff, self.max_backoff)
        # Add jitter (±25%)
        jitter = backoff * 0.25 * (random.random() * 2 - 1)
        return backoff + jitter
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        return urlparse(url).netloc.lower()
    
    def _is_blocked(self, domain: str) -> bool:
        """Check if domain is blocked"""
        if domain in self._blacklisted_domains:
            return True
        
        stats = self._domain_stats.get(domain)
        if stats and stats.is_blocked:
            return True
        
        return False
    
    def unblock_domain(self, domain: str):
        """Manually unblock a domain"""
        self._blacklisted_domains.discard(domain)
        if domain in self._domain_stats:
            self._domain_stats[domain].is_blocked = False
            self._domain_stats[domain].consecutive_failures = 0
            self._domain_stats[domain].backoff_until = None
    
    def get_stats(self) -> Dict[str, Dict]:
        """Get all domain statistics"""
        return {
            domain: {
                "total_requests": stats.total_requests,
                "successful": stats.successful,
                "failed": stats.failed,
                "success_rate": stats.successful / max(stats.total_requests, 1),
                "is_blocked": stats.is_blocked,
                "consecutive_failures": stats.consecutive_failures
            }
            for domain, stats in self._domain_stats.items()
        }
    
    def get_blocked_domains(self) -> List[str]:
        """Get list of blocked domains"""
        return list(self._blacklisted_domains)


# Global controller instance
scrape_controller = ScrapeController()
