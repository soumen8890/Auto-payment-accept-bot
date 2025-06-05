import hashlib
import hmac
import json
from typing import Dict, Optional
from config import payment_config

def verify_bharatpe_webhook_signature(payload: Dict, signature: str) -> bool:
    """Verify BharatPe webhook signature"""
    secret = payment_config.BHARATPE_WEBHOOK_SECRET.encode()
    payload_str = json.dumps(payload, separators=(',', ':')).encode()
    
    computed_signature = hmac.new(
        secret,
        payload_str,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_signature, signature)

def generate_paytm_checksum(params: Dict, merchant_key: str) -> str:
    """Generate PayTM checksum for transaction verification"""
    sorted_params = {k: v for k, v in sorted(params.items())}
    param_str = '|'.join(f"{k}={v}" for k, v in sorted_params.items())
    param_str += f"|{merchant_key}"
    
    return hashlib.sha256(param_str.encode()).hexdigest()

def mask_sensitive_data(data: Dict) -> Dict:
    """Mask sensitive payment information for logging"""
    masked = data.copy()
    sensitive_fields = ['card_number', 'cvv', 'password', 'token']
    
    for field in sensitive_fields:
        if field in masked:
            masked[field] = '****'
    
    if 'upi_id' in masked:
        masked['upi_id'] = masked['upi_id'][0:3] + '****' + masked['upi_id'][-2:]
    
    return masked
