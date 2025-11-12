"""
Configuration Module
Centralized configuration management with presets support
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Optional

# Explicitly load .env file from project root
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    # Fallback to current directory
    load_dotenv()


class Config:
    """Configuration manager with preset support"""
    
    # API Configuration
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
    
    # Git Analysis Settings
    DEFAULT_COMMIT_LIMIT = int(os.getenv("DEFAULT_COMMIT_LIMIT", "20"))
    SESSION_GAP_HOURS = int(os.getenv("SESSION_GAP_HOURS", "3"))
    
    # Output Formats
    OUTPUT_FORMATS = ["standup", "technical", "weekly", "insights"]
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    OUTPUT_DIR = PROJECT_ROOT / "output"
    CACHE_DIR = PROJECT_ROOT / ".cache"
    CONFIG_DIR = PROJECT_ROOT / "config"
    
    # Cache Settings
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_MAX_AGE_HOURS = int(os.getenv("CACHE_MAX_AGE_HOURS", "24"))
    CACHE_MAX_AGE_DAYS = int(os.getenv("CACHE_MAX_AGE_DAYS", "7"))
    
    # Quality Scoring
    QUALITY_THRESHOLD_LOW = 0.6
    QUALITY_THRESHOLD_HIGH = 0.8
    SIZE_SMALL = 50
    SIZE_MEDIUM = 200
    SIZE_LARGE = 500
    
    # Webhook Settings
    WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "5000"))
    WEBHOOK_ENABLED = os.getenv("WEBHOOK_ENABLED", "false").lower() == "true"
    
    # Slack Integration
    SLACK_TOKEN = os.getenv("SLACK_TOKEN")
    SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#standup")
    SLACK_ENABLED = os.getenv("SLACK_ENABLED", "false").lower() == "true"
    
    # Vector Search
    VECTOR_SEARCH_ENABLED = True
    VECTOR_MODEL = "all-MiniLM-L6-v2"
    VECTOR_TOP_K = 5
    
    @classmethod
    def load_preset(cls, preset_name: str) -> Optional[Dict]:
        """Load configuration preset from YAML"""
        preset_file = cls.CONFIG_DIR / "presets.yaml"
        
        if not preset_file.exists():
            return None
        
        try:
            with open(preset_file, 'r') as f:
                presets = yaml.safe_load(f)
                return presets.get('profiles', {}).get(preset_name)
        except Exception as e:
            print(f"Warning: Could not load preset '{preset_name}': {e}")
            return None
    
    @classmethod
    def apply_preset(cls, preset_name: str):
        """Apply preset configuration"""
        preset = cls.load_preset(preset_name)
        
        if not preset:
            print(f"Preset '{preset_name}' not found, using defaults")
            return
        
        if 'commits' in preset:
            cls.DEFAULT_COMMIT_LIMIT = preset['commits']
        if 'formats' in preset:
            cls.OUTPUT_FORMATS = preset['formats']
        
        print(f"[OK] Applied preset: {preset_name}")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration"""
        if not cls.ANTHROPIC_API_KEY:
            print("[ERROR] ANTHROPIC_API_KEY not set")
            return False
        
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.CACHE_DIR.mkdir(exist_ok=True)
        return True


if __name__ != "__main__":
    Config.validate()
