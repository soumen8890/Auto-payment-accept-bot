import re
from typing import Optional

def validate_phone(phone: str) -> Optional[str]:
    """Validate Indian phone number"""
    pattern = r'^[6-9]\d{9}$'
    if re.match(pattern, phone):
        return phone
    return None

def validate_email(email: str) -> Optional[str]:
    """Validate email address"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return email
    return None

def validate_upi(upi_id: str) -> Optional[str]:
    """Validate UPI ID"""
    pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$'
    if re.match(pattern, upi_id):
        return upi_id
    return None

def validate_amount(amount: str) -> Optional[float]:
    """Validate payment amount"""
    try:
        amount_float = float(amount)
        if amount_float > 0:
            return amount_float
    except ValueError:
        pass
    return None
