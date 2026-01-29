"""
System Status Constants
Sprint 16 - Task 126

Declares the official system version and status.
"""

# System Version
SYSTEM_VERSION = "1.0"
SYSTEM_STATUS = "STABLE"

# Feature Freeze
FEATURE_FREEZE_ACTIVE = True
FEATURE_FREEZE_DATE = "2026-01-29"

# Deployment Modes
DEPLOYMENT_MODE_LOCAL = "local"
DEPLOYMENT_MODE_PRODUCTION = "production"

# Status Descriptions
STATUS_DESCRIPTIONS = {
    "STABLE": "Production-ready, feature-frozen, maintenance mode",
    "DEVELOPMENT": "Active development, not production-ready",
    "DEPRECATED": "No longer maintained, use newer version",
}

# Version History
VERSION_HISTORY = {
    "1.0": {
        "release_date": "2026-01-29",
        "status": "STABLE",
        "description": "Initial production release with full hardening",
        "key_features": [
            "5-layer adaptive scraping",
            "Human-in-the-loop quality assurance",
            "Hard resource limits (WSL-safe)",
            "Graceful failure recovery",
            "Comprehensive operational monitoring",
            "Mode-based configuration",
        ],
        "breaking_changes": [],
    }
}

# Future Triggers (from SYSTEM_FREEZE.md)
DEVELOPMENT_TRIGGERS = {
    "paid_demand": "3+ paid clients request same feature",
    "repeated_jobs": "Same job type run 10+ times with workarounds",
    "infrastructure_upgrade": "Move to significantly better infrastructure",
    "role_requirement": "Job change requires system enhancement",
    "security_issue": "Critical vulnerability discovered",
}


def get_system_info() -> dict:
    """Get current system information."""
    return {
        "version": SYSTEM_VERSION,
        "status": SYSTEM_STATUS,
        "status_description": STATUS_DESCRIPTIONS.get(SYSTEM_STATUS, "Unknown"),
        "feature_freeze": FEATURE_FREEZE_ACTIVE,
        "freeze_date": FEATURE_FREEZE_DATE if FEATURE_FREEZE_ACTIVE else None,
    }


def is_production_ready() -> bool:
    """Check if system is production-ready."""
    return SYSTEM_STATUS == "STABLE"


def is_feature_frozen() -> bool:
    """Check if feature freeze is active."""
    return FEATURE_FREEZE_ACTIVE
