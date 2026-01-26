"""
Robots.txt API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import RobotsCheckRequest, RobotsCheckResponse
from app.services.robots_checker import robots_checker

router = APIRouter()


@router.post("/check", response_model=RobotsCheckResponse)
async def check_robots(
    request: RobotsCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Check robots.txt compliance for a domain
    """
    try:
        result = await robots_checker.check_url_allowed(
            f"https://{request.domain}",
            db=db
        )

        return RobotsCheckResponse(
            domain=request.domain,
            allowed=result["allowed"],
            crawl_delay=result["crawl_delay"],
            sitemap_urls=result["sitemap_urls"],
            checked_at=result["checked_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking robots.txt: {str(e)}")


@router.get("/delay/{domain}")
async def get_crawl_delay(domain: str, db: AsyncSession = Depends(get_db)):
    """
    Get respectful crawl delay for a domain
    """
    try:
        delay = await robots_checker.get_respectful_delay(f"https://{domain}", db=db)
        return {"domain": domain, "crawl_delay_seconds": delay}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting crawl delay: {str(e)}")