import re
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
import pytz
from config import settings

def format_currency(amount: float) -> str:
    """Format currency with Indian Rupee symbol and proper formatting"""
    return f"₹{amount:,.2f}"

def parse_timedelta(time_str: str) -> Optional[timedelta]:
    """
    Parse a time string (e.g., '1d', '2h', '30m') into a timedelta object
    """
    regex = re.compile(r'^((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?$')
    parts = regex.match(time_str.lower())
    if not parts:
        return None
    
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    
    return timedelta(**time_params)

def format_timedelta(delta: timedelta) -> str:
    """Convert timedelta to human-readable format"""
    total_seconds = delta.total_seconds()
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days:
        parts.append(f"{int(days)} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{int(hours)} hour{'s' if hours != 1 else ''}")
    if minutes and not days:  # Only show minutes if < 1 hour
        parts.append(f"{int(minutes)} minute{'s' if minutes != 1 else ''}")
    
    return ', '.join(parts) if parts else "less than a minute"

def get_ist_time() -> datetime:
    """Get current time in Indian Standard Time"""
    return datetime.now(pytz.timezone('Asia/Kolkata'))

def deep_get(dictionary: Dict[str, Any], keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary keys"""
    keys = keys.split('.')
    for key in keys:
        if isinstance(dictionary, dict) and key in dictionary
