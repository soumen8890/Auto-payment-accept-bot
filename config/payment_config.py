from config.settings import settings

class PaymentConfig:
    # BharatPe Configuration
    BHARATPE_API_URL = "https://api.bharatpe.com/v1"
    BHARATPE_API_KEY = os.getenv('BHARATPE_API_KEY')
    BHARATPE_CALLBACK_URL = os.getenv('BHARATPE_CALLBACK_URL')
    
    # PayTM Configuration
    PAYTM_MERCHANT_ID = os.getenv('PAYTM_MERCHANT_ID')
    PAYTM_MERCHANT_KEY = os.getenv('PAYTM_MERCHANT_KEY')
    PAYTM_WEBSITE = os.getenv('PAYTM_WEBSITE', 'WEBSTAGING')
    PAYTM_CALLBACK_URL = os.getenv('PAYTM_CALLBACK_URL')
    PAYTM_TXN_URL = (
        "https://securegw-stage.paytm.in/theia/processTransaction"
        if settings.DEBUG
        else "https://securegw.paytm.in/theia/processTransaction"
    )
    
    # Payment Methods
    PAYMENT_METHODS = {
        'bharatpe': {
            'name': 'BharatPe UPI',
            'min_amount': 10,
            'max_amount': 100000
        },
        'paytm': {
            'name': 'PayTM Wallet/UPI',
            'min_amount': 1,
            'max_amount': 100000
        }
    }

payment_config = PaymentConfig()
