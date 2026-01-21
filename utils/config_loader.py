"""
Configuration Loading and Management
Centralized configuration handling
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and manage application configuration"""
    
    DEFAULT_CONFIG = {
        "pixel_size_mm": 0.1,
        "threshold_method": "otsu",
        "normalization_method": "clahe",
        "min_hole_diameter_mm": 1.0,
        "max_hole_diameter_mm": 30.0,
        "output_dir": "./output",
        "processed_dir": "./processed",
        "results_dir": "./results",
        "unprocessed_dir": "./unprocessed"
    }
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    return {**self.DEFAULT_CONFIG, **loaded}
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load config file: {e}. Using defaults.")
        
        return self.DEFAULT_CONFIG.copy()
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def save(self) -> None:
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        logger.info(f"Configuration saved to {self.config_path}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self.config.copy()


# Global config loader instance
_config_loader_instance = None


def get_config() -> ConfigLoader:
    """Get global config loader instance (singleton)"""
    global _config_loader_instance
    if _config_loader_instance is None:
        _config_loader_instance = ConfigLoader()
    return _config_loader_instance
