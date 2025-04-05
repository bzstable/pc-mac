"""
Configuration management utilities.
Handles API keys, user preferences, and other settings.
"""

from pathlib import Path
import json
from typing import Dict, Optional
import os

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".ccos"
        self.config_file = self.config_dir / "config.json"
        self.default_config = {
            "perplexity_api_key": None,
            "theme_color": "#00c5e0",
            "max_context_length": 4000,
            "default_model": "sonar-reasoning-pro"
        }
        self._ensure_config_exists()
        
    def _ensure_config_exists(self):
        """Ensure config directory and file exist."""
        self.config_dir.mkdir(exist_ok=True)
        if not self.config_file.exists():
            self.config_file.write_text(json.dumps(self.default_config, indent=2))
            
    def load_config(self) -> Dict:
        """Load configuration from file."""
        try:
            return json.loads(self.config_file.read_text())
        except Exception:
            return self.default_config.copy()
            
    def save_config(self, config: Dict):
        """Save configuration to file."""
        self.config_file.write_text(json.dumps(config, indent=2))
        
    def get_api_key(self) -> Optional[str]:
        """Get Perplexity API key."""
        config = self.load_config()
        return config.get("perplexity_api_key") or os.getenv("PERPLEXITY_API_KEY")
        
    def set_api_key(self, api_key: str):
        """Set Perplexity API key."""
        config = self.load_config()
        config["perplexity_api_key"] = api_key
        self.save_config(config)
        
    def get_setting(self, key: str) -> Optional[str]:
        """Get a specific setting value."""
        config = self.load_config()
        return config.get(key)
        
    def set_setting(self, key: str, value: str):
        """Set a specific setting value."""
        config = self.load_config()
        config[key] = value
        self.save_config(config)
        
    def reset_config(self):
        """Reset configuration to defaults."""
        self.save_config(self.default_config) 