"""
PRO FEATURE: ROTATING PROXY MANAGER
Handles residential and datacenter proxies with automated health checks and rotation.
"""
import random
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from app.core.config import settings

@dataclass
class ProxyNode:
    url: str
    proxy_type: str = "datacenter"  # datacenter, residential, mobile
    failure_count: int = 0
    last_used: float = 0
    is_active: bool = True
    cooldown_until: float = 0

class ProxyManager:
    """
    Manages a pool of proxies with health checks and rotation strategies.
    
    If no proxies are configured, it returns None (direct connection).
    """
    
    def __init__(self):
        self._proxies: List[ProxyNode] = []
        self._load_proxies()
        
    def _load_proxies(self):
        """Load proxies from settings or external source"""
        # Load from CONFIG (simple list for now)
        raw_proxies = getattr(settings, "PROXY_LIST", [])
        if settings.PROXY_URL:
            raw_proxies.append(settings.PROXY_URL)
            
        for url in raw_proxies:
            self._proxies.append(ProxyNode(url=url))
            
    def get_proxy(self, domain: Optional[str] = None) -> Optional[str]:
        """
        Get a proxy based on availability and domain-specific health.
        """
        if not self._proxies:
            return None
            
        now = time.time()
        available = [
            p for p in self._proxies 
            if p.is_active and p.cooldown_until < now
        ]
        
        if not available:
            # If everything is on cooldown, pick the oldest one
            return random.choice(self._proxies).url if self._proxies else None
            
        # Strategy: Least recently used among available
        choice = min(available, key=lambda x: x.last_used)
        choice.last_used = now
        return choice.url

    def report_failure(self, proxy_url: str):
        """Mark a proxy as failed and trigger cooldown"""
        for p in self._proxies:
            if p.url == proxy_url:
                p.failure_count += 1
                # Exponential cooldown: 30s, 60s, 120s...
                p.cooldown_until = time.time() + (30 * (2 ** (p.failure_count - 1)))
                if p.failure_count > 5:
                    p.is_active = False
                break

    def report_success(self, proxy_url: str):
        """Reset failure count on success"""
        for p in self._proxies:
            if p.url == proxy_url:
                p.failure_count = 0
                p.is_active = True
                break

# Global singleton
proxy_manager = ProxyManager()
