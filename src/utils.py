"""
Utility Functions
Common helper functions used across modules
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import hashlib
import json
import re


def format_duration(td: timedelta) -> str:
    """Format timedelta as human-readable string"""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    
    return " ".join(parts) if parts else "Less than a minute"


def hash_string(text: str, length: int = 6) -> str:
    """Generate short hash of string"""
    return hashlib.md5(text.encode()).hexdigest()[:length]


def safe_json_loads(text: str, default: Any = None) -> Any:
    """Safely parse JSON with fallback"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return default


def extract_json_from_text(text: str) -> Dict:
    """Extract JSON from text that may contain other content"""
    result = safe_json_loads(text, None)
    if result is not None:
        return result
    
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    for match in matches:
        result = safe_json_loads(match, None)
        if result is not None:
            return result
    
    return {}


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def group_by_key(items: List[Dict], key: str) -> Dict[Any, List[Dict]]:
    """Group list of dicts by key value"""
    from collections import defaultdict
    grouped = defaultdict(list)
    
    for item in items:
        if key in item:
            grouped[item[key]].append(item)
    
    return dict(grouped)


def percentage(part: float, whole: float) -> float:
    """Calculate percentage safely"""
    if whole == 0:
        return 0.0
    return (part / whole) * 100


def format_timestamp(dt: datetime, format: str = "human") -> str:
    """Format datetime for display"""
    if format == "human":
        return dt.strftime("%B %d, %Y at %I:%M %p")
    elif format == "iso":
        return dt.isoformat()
    elif format == "short":
        return dt.strftime("%Y-%m-%d %H:%M")
    else:
        return str(dt)


class ProgressTracker:
    """Simple progress tracker for long operations"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
    
    def update(self, increment: int = 1):
        """Update progress"""
        self.current += increment
        self._display()
    
    def _display(self):
        """Display progress bar"""
        if self.total == 0:
            return
        
        percentage = (self.current / self.total) * 100
        bar_length = 40
        filled = int(bar_length * self.current / self.total)
        bar = "#" * filled + "." * (bar_length - filled)
        
        print(f"\r{self.description}: [{bar}] {percentage:.1f}%", end="", flush=True)
        
        if self.current >= self.total:
            print()


def validate_commit_data(commit: Dict) -> bool:
    """Validate that commit dict has required fields"""
    required_fields = ['hash', 'message', 'timestamp', 'author']
    return all(field in commit for field in required_fields)
