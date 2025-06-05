import requests
from config.config import BHARATPE_API_KEY

def verify_utr(utr_number):
    headers = {
        'Authorization': f'Bearer {BHARATPE_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(
        f'https://api.bharatpe.com/v1/utr/verify?utr={utr_number}',
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    return None
