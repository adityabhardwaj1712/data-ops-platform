"""
Notifications API endpoints
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional

from app.services.notifications import notification_service, NotificationType

router = APIRouter()


@router.get("/")
async def get_notifications(
    type: Optional[str] = None,
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200)
):
    """Get notifications"""
    notification_type = NotificationType(type) if type else None
    return notification_service.get_notifications(
        notification_type=notification_type,
        unread_only=unread_only,
        limit=limit
    )


@router.get("/unread/count")
async def get_unread_count():
    """Get count of unread notifications"""
    return {"count": notification_service.get_unread_count()}


@router.post("/{notification_id}/read")
async def mark_as_read(notification_id: int):
    """Mark a notification as read"""
    notification_service.mark_as_read(notification_id)
    return {"success": True}


@router.post("/read-all")
async def mark_all_as_read():
    """Mark all notifications as read"""
    notification_service.mark_all_as_read()
    return {"success": True}
