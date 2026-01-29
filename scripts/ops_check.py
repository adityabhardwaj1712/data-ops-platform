#!/usr/bin/env python3
"""
Operational Check Commands
Sprint 15 - Task 119

Provides CLI commands for operational health checks:
- Health check
- Worker status
- Queue depth
- Disk usage (artifacts)
"""
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any
import psutil
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.limits import limits, get_mode_specific_limits, get_effective_browser_limit
from app.db.database import get_db
from app.db.models import Job, JobStatus
from sqlalchemy import select, func


async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check of the system.
    
    Returns:
        Dictionary with health status
    """
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # System resources
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    
    health["checks"]["memory"] = {
        "total_mb": round(memory.total / (1024 * 1024), 2),
        "used_mb": round(memory.used / (1024 * 1024), 2),
        "available_mb": round(memory.available / (1024 * 1024), 2),
        "percent": memory.percent,
        "status": "ok" if memory.percent < 85 else "warning"
    }
    
    health["checks"]["disk"] = {
        "total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
        "used_gb": round(disk.used / (1024 * 1024 * 1024), 2),
        "free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
        "percent": disk.percent,
        "status": "ok" if disk.percent < 85 else "warning"
    }
    
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    health["checks"]["cpu"] = {
        "percent": cpu_percent,
        "count": psutil.cpu_count(),
        "status": "ok" if cpu_percent < 80 else "warning"
    }
    
    # Deployment mode
    mode_limits = get_mode_specific_limits()
    health["checks"]["deployment_mode"] = {
        "mode": limits.DEPLOYMENT_MODE,
        "max_workers": mode_limits["max_workers"],
        "max_browser_instances": mode_limits["max_browser_instances"],
        "browser_parallelism": mode_limits["browser_parallelism"],
        "status": "ok"
    }
    
    # Database connectivity
    try:
        async for db in get_db():
            # Simple query to test connection
            result = await db.execute(select(func.count(Job.id)))
            job_count = result.scalar()
            health["checks"]["database"] = {
                "connected": True,
                "total_jobs": job_count,
                "status": "ok"
            }
            break
    except Exception as e:
        health["checks"]["database"] = {
            "connected": False,
            "error": str(e),
            "status": "error"
        }
        health["status"] = "degraded"
    
    # Overall status
    if any(check.get("status") == "error" for check in health["checks"].values()):
        health["status"] = "unhealthy"
    elif any(check.get("status") == "warning" for check in health["checks"].values()):
        health["status"] = "degraded"
    
    return health


async def worker_status() -> Dict[str, Any]:
    """
    Get status of worker processes.
    
    Returns:
        Dictionary with worker status
    """
    status = {
        "timestamp": datetime.utcnow().isoformat(),
        "workers": [],
        "summary": {}
    }
    
    # Find Python worker processes
    current_process = psutil.Process()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'cpu_percent']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('worker' in arg.lower() for arg in cmdline):
                    memory_mb = proc.info['memory_info'].rss / (1024 * 1024)
                    status["workers"].append({
                        "pid": proc.info['pid'],
                        "memory_mb": round(memory_mb, 2),
                        "cpu_percent": proc.info.get('cpu_percent', 0),
                        "status": "running"
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Summary
    mode_limits = get_mode_specific_limits()
    status["summary"] = {
        "active_workers": len(status["workers"]),
        "max_workers": mode_limits["max_workers"],
        "total_memory_mb": round(sum(w["memory_mb"] for w in status["workers"]), 2),
        "max_memory_per_worker_mb": limits.MAX_WORKER_MEMORY_MB
    }
    
    return status


async def queue_depth() -> Dict[str, Any]:
    """
    Get depth of job queue.
    
    Returns:
        Dictionary with queue statistics
    """
    queue_stats = {
        "timestamp": datetime.utcnow().isoformat(),
        "by_status": {},
        "summary": {}
    }
    
    try:
        async for db in get_db():
            # Count jobs by status
            for status in JobStatus:
                result = await db.execute(
                    select(func.count(Job.id)).where(Job.status == status)
                )
                count = result.scalar()
                queue_stats["by_status"][status.value] = count
            
            # Summary
            total_jobs = sum(queue_stats["by_status"].values())
            active_jobs = (
                queue_stats["by_status"].get(JobStatus.PENDING.value, 0) +
                queue_stats["by_status"].get(JobStatus.RUNNING.value, 0) +
                queue_stats["by_status"].get(JobStatus.SCRAPING.value, 0) +
                queue_stats["by_status"].get(JobStatus.PROCESSING.value, 0)
            )
            
            queue_stats["summary"] = {
                "total_jobs": total_jobs,
                "active_jobs": active_jobs,
                "max_concurrent_jobs": limits.MAX_CONCURRENT_JOBS,
                "queue_utilization_percent": round((active_jobs / limits.MAX_CONCURRENT_JOBS) * 100, 2) if limits.MAX_CONCURRENT_JOBS > 0 else 0
            }
            break
    except Exception as e:
        queue_stats["error"] = str(e)
    
    return queue_stats


async def disk_usage_artifacts() -> Dict[str, Any]:
    """
    Get disk usage for artifacts directory.
    
    Returns:
        Dictionary with artifact storage statistics
    """
    artifacts_path = Path("/app/data/artifacts")
    
    usage = {
        "timestamp": datetime.utcnow().isoformat(),
        "artifacts_path": str(artifacts_path),
        "exists": artifacts_path.exists(),
        "storage": {}
    }
    
    if artifacts_path.exists():
        total_size = 0
        file_count = 0
        job_dirs = 0
        
        for item in artifacts_path.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
                file_count += 1
            elif item.is_dir() and item.parent == artifacts_path:
                job_dirs += 1
        
        usage["storage"] = {
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_size_gb": round(total_size / (1024 * 1024 * 1024), 2),
            "file_count": file_count,
            "job_directories": job_dirs,
            "max_per_job_mb": limits.MAX_ARTIFACT_STORAGE_MB
        }
        
        # Check if approaching limits
        avg_per_job = (total_size / job_dirs / (1024 * 1024)) if job_dirs > 0 else 0
        usage["storage"]["avg_per_job_mb"] = round(avg_per_job, 2)
        
        if avg_per_job > limits.MAX_ARTIFACT_STORAGE_MB * 0.8:
            usage["storage"]["warning"] = f"Average job storage approaching limit ({limits.MAX_ARTIFACT_STORAGE_MB} MB)"
    
    return usage


async def main():
    """
    Main CLI entry point.
    """
    if len(sys.argv) < 2:
        print("Usage: python ops_check.py [health|workers|queue|disk|all]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "health":
        result = await health_check()
    elif command == "workers":
        result = await worker_status()
    elif command == "queue":
        result = await queue_depth()
    elif command == "disk":
        result = await disk_usage_artifacts()
    elif command == "all":
        result = {
            "health": await health_check(),
            "workers": await worker_status(),
            "queue": await queue_depth(),
            "disk": await disk_usage_artifacts()
        }
    else:
        print(f"Unknown command: {command}")
        print("Available commands: health, workers, queue, disk, all")
        sys.exit(1)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
