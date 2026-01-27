"""
Feature Flags System
Centralized feature management with lazy loading
"""

from app.core.config import settings
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FeatureFlags:
    """
    Centralized feature flag management.
    
    Features are loaded lazily - only when first accessed.
    This keeps the application lightweight.
    """
    
    def __init__(self):
        self._loaded_features: Dict[str, Any] = {}
    
    def is_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        feature_map = {
            "visualization": settings.ENABLE_VISUALIZATION,
            "ai_copilot": settings.ENABLE_AI_COPILOT,
            "quality_checks": settings.ENABLE_QUALITY_CHECKS,
            "cost_analytics": settings.ENABLE_COST_ANALYTICS,
            "sso": settings.ENABLE_SSO,
            "audit_logs": settings.ENABLE_AUDIT_LOGS,
            "multi_tenancy": settings.ENABLE_MULTI_TENANCY,
            "anomaly_detection": settings.ENABLE_ANOMALY_DETECTION,
            "advanced_charts": settings.ENABLE_ADVANCED_CHARTS,
        }
        return feature_map.get(feature, False)
    
    def get_feature(self, feature: str) -> Optional[Any]:
        """
        Get a feature instance (lazy-loaded).
        
        Features are imported and instantiated only when first requested.
        This keeps memory usage low.
        """
        if feature in self._loaded_features:
            return self._loaded_features[feature]
        
        if not self.is_enabled(feature):
            logger.warning(f"Feature '{feature}' is not enabled")
            return None
        
        # Lazy load feature
        try:
            if feature == "ai_copilot":
                from app.features.ai_copilot import AICopilot
                self._loaded_features[feature] = AICopilot()
                logger.info(f"Loaded feature: {feature}")
            
            elif feature == "quality_checks":
                from app.features.quality import QualityEngine
                self._loaded_features[feature] = QualityEngine()
                logger.info(f"Loaded feature: {feature}")
            
            elif feature == "visualization":
                from app.features.visualization import VisualizationEngine
                self._loaded_features[feature] = VisualizationEngine()
                logger.info(f"Loaded feature: {feature}")
            
            elif feature == "cost_analytics":
                from app.features.cost_analytics import CostAnalytics
                self._loaded_features[feature] = CostAnalytics()
                logger.info(f"Loaded feature: {feature}")
            
            return self._loaded_features.get(feature)
        
        except ImportError as e:
            logger.error(f"Failed to load feature '{feature}': {e}")
            return None
    
    def get_enabled_features(self) -> list:
        """Get list of enabled features."""
        return [
            feature for feature in [
                "visualization",
                "ai_copilot",
                "quality_checks",
                "cost_analytics",
                "sso",
                "audit_logs",
                "multi_tenancy",
            ]
            if self.is_enabled(feature)
        ]


# Global feature flags instance
feature_flags = FeatureFlags()
