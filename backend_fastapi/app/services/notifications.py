"""
Notification Service
Send notifications for job completion, errors, etc.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    TASK_FAILED = "task_failed"
    LOW_CONFIDENCE = "low_confidence"
    EXPORT_READY = "export_ready"
    SYSTEM_ALERT = "system_alert"


class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self):
        self.notifications: List[Dict[str, Any]] = []
        self.max_notifications = 1000  # Keep last 1000 notifications
    
    def create_notification(
        self,
        notification_type: NotificationType,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new notification"""
        notification = {
            "id": len(self.notifications) + 1,
            "type": notification_type.value,
            "title": title,
            "message": message,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "read": False
        }
        
        self.notifications.append(notification)
        
        # Keep only last N notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[-self.max_notifications:]
        
        logger.info(f"Created notification: {title}")
        
        return notification
    
    def get_notifications(
        self,
        notification_type: Optional[NotificationType] = None,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get notifications"""
        filtered = self.notifications
        
        if notification_type:
            filtered = [n for n in filtered if n["type"] == notification_type.value]
        
        if unread_only:
            filtered = [n for n in filtered if not n["read"]]
        
        return filtered[-limit:]
    
    def mark_as_read(self, notification_id: int):
        """Mark a notification as read"""
        for notification in self.notifications:
            if notification["id"] == notification_id:
                notification["read"] = True
                return
    
    def mark_all_as_read(self):
        """Mark all notifications as read"""
        for notification in self.notifications:
            notification["read"] = True
    
    def get_unread_count(self) -> int:
        """Get count of unread notifications"""
        return sum(1 for n in self.notifications if not n["read"])


# Global instance
notification_service = NotificationService()
