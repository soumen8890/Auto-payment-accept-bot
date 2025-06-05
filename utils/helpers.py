import re
from datetime import datetime, timedelta
from typing import Optional, Union

def validate_phone_number(phone: str) -> bool:
    """Validate Indian phone numbers"""
    return bool(re.match(r'^[6-9]\d{9}$
