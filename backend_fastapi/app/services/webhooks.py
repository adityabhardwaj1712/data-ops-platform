"""
PRO FEATURE: WEBHOOK SERVICE
Automates data delivery to external endpoints (Slack, Databases, third-party APIs).
"""
import httpx
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class WebhookService:
    """
    Sends scraped data to external webhooks.
    Complete 'hands-off' automation.
    """
    
    async def send(
        self, 
        url: str, 
        payload: Dict[str, Any], 
        secret: Optional[str] = None
    ) -> bool:
        """
        Send payload to a webhook URL.
        """
        if not url:
            return False
            
        # Enrich payload with metadata
        data = {
            "source": "data-ops-platform",
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Platform-Source": "SentinelOps-Scraper"
        }
        
        # Add signature if secret is provided (future proofing)
        if secret:
            headers["X-Webhook-Signature"] = self._generate_signature(data, secret)
            
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()
                logger.info(f"Webhook sent successfully to {url}")
                return True
        except Exception as e:
            logger.error(f"Failed to send webhook to {url}: {str(e)}")
            # In a pro system, we would queue this for retry
            return False

    def _generate_signature(self, data: Dict[str, Any], secret: str) -> str:
        """Sign payload with secret key"""
        import hmac
        import hashlib
        import json
        
        payload_str = json.dumps(data, sort_keys=True)
        return hmac.new(
            secret.encode(), 
            payload_str.encode(), 
            hashlib.sha256
        ).hexdigest()

# Global singleton
webhook_service = WebhookService()
