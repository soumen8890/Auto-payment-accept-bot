import requests
import hashlib
import json
import logging
from urllib.parse import urlencode
from config import payment_config
from database.repositories import PaymentRepository

logger = logging.getLogger(__name__)

class PaytmService:
    def __init__(self, db):
        self.merchant_id = payment_config.PAYTM_MERCHANT_ID
        self.merchant_key = payment_config.PAYTM_MERCHANT_KEY
        self.website = payment_config.PAYTM_WEBSITE
        self.callback_url = payment_config.PAYTM_CALLBACK_URL
        self.payment_repo = PaymentRepository(db)

    def generate_checksum(self, params: dict) -> str:
        """Generate PayTM checksum for transaction security"""
        params_str = urlencode(params)
        salt = self.merchant_key
        checksum = hashlib.sha256((params_str + salt).encode()).hexdigest()
        return checksum

    async def initiate_transaction(self, user_id: int, amount: float, order_id: str):
        """Initiate PayTM payment transaction"""
        params = {
            'MID': self.merchant_id,
            'WEBSITE': self.website,
            'ORDER_ID': order_id,
            'CUST_ID': str(user_id),
            'TXN_AMOUNT': str(amount),
            'CHANNEL_ID': 'WEB',
            'INDUSTRY_TYPE_ID': 'Retail',
            'CALLBACK_URL': self.callback_url
        }
        
        params['CHECKSUMHASH'] = self.generate_checksum(params)
        
        return {
            'url': payment_config.PAYTM_TXN_URL,
            'params': params
        }

    async def verify_transaction(self, transaction_id: str) -> bool:
        """Verify PayTM transaction status"""
        endpoint = f"{payment_config.PAYTM_API_URL}/v3/order/status"
        
        params = {
            'MID': self.merchant_id,
            'ORDERID': transaction_id
        }
        params['CHECKSUMHASH'] = self.generate_checksum(params)
        
        try:
            response = requests.post(
                endpoint,
                json=params,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get('STATUS') == 'TXN_SUCCESS':
                logger.info(f"PayTM transaction {transaction_id} verified")
                return True
                
            logger.warning(f"PayTM verification failed: {data}")
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"PayTM API error: {str(e)}")
            return False

    async def process_paytm_webhook(self, payload: dict):
        """Process PayTM payment webhook"""
        transaction_id = payload.get('ORDERID')
        status = payload.get('STATUS')
        
        payment = self.payment_repo.get_payment_by_transaction_id(transaction_id)
        if not payment:
            logger.error(f"Payment not found for transaction: {transaction_id}")
            return False
        
        if status == 'TXN_SUCCESS':
            self.payment_repo.update_payment_status(payment.id, 'completed')
            logger.info(f"Payment {transaction_id} completed via webhook")
            return True
            
        logger.warning(f"Webhook processing failed for {transaction_id}")
        return False
