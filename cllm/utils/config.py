import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """Manages persistent configurations for the CLI."""
    
    def __init__(self):
        """Initializes the configuration manager."""
        self.config_dir = Path.home() / ".config" / "cllm"
        self.config_file = self.config_dir / "config.json"
        self.ensure_config_dir()
        self.settings = self.load_config()
    
    def ensure_config_dir(self) -> None:
        """Ensures that the configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self) -> Dict[str, Any]:
        """Loads the configurations from the file."""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    
    def save_config(self) -> None:
        """Saves the configurations to the file."""
        with open(self.config_file, "w") as f:
            json.dump(self.settings, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Gets a value from the configuration."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Sets a value in the configuration."""
        self.settings[key] = value
        self.save_config()
    
    def get_api_key(self) -> Optional[str]:
        """Gets the OpenAI API key."""
        # Priority: environment variable > configuration file
        return os.environ.get("OPENAI_API_KEY") or self.get("api_key")
    
    def set_api_key(self, api_key: str) -> None:
        """Sets the OpenAI API key."""
        self.set("api_key", api_key)