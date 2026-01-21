"""
Config Repository
Data access for configuration
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from utils.exceptions import ConfigurationError
import logging

logger = logging.getLogger(__name__)


class ConfigRepository:
    """Manages persistence of configuration data"""
    
    DEFAULT_CONFIG = {
        "pixel_size_mm": 0.1,
        "threshold_method": "otsu",
        "normalization_method": "clahe",
        "min_hole_diameter_mm": 1.0,
        "max_hole_diameter_mm": 30.0
    }
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = self._load_from_file()
    
    def _load_from_file(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    return {**self.DEFAULT_CONFIG, **loaded}
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load config file: {e}. Using defaults.")
        
        return self.DEFAULT_CONFIG.copy()
    
    def _save_to_file(self) -> None:
        """Save configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.debug(f"Saved configuration to {self.config_path}")
        except IOError as e:
            logger.error(f"Failed to save config: {e}")
            raise ConfigurationError(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self._config.update(updates)
    
    def save(self) -> None:
        """Save configuration to file"""
        self._save_to_file()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self._config = self.DEFAULT_CONFIG.copy()
        self._save_to_file()
        logger.info("Configuration reset to defaults")
