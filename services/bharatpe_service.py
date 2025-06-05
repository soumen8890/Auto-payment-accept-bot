import requests
import logging
from datetime import datetime
from config import payment_config
from utils.helpers import retry
from database.repositories import PaymentRepository

logger = logging.getLogger(__name__)

class BharatPeService:
    def __init__(self, db):
        self.base_url = payment_config.BHARATPE_API_URL
        self.headers = {
            'Authorization': f'Bearer {payment_config.BHARATPE_API_KEY}',
            'Content-Type': 'application/json'
        }
        self.payment_repo = PaymentRepository(db)

    @retry(max_attempts=3, delay=1)
    async def verify_utr(self, utr_number: str, expected_amount: float) -> bool:
        """Verify UTR payment with BharatPe API"""
        try:
            endpoint = f"{self.base_url}/transactions/{utr_number}"
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            
            if (data.get('status') == 'SUCCESS' and 
                float(data.get('amount')) == expected_amount):
                logger.info(f"UTR {utr_number} verified successfully")
                return True
                
            logger.warning(f"UTR verification failed: {data}")
            return False
            
        except requests.exceptions.RequestException as e:
            logger.error(f"BharatPe API error: {str(e)}")
            return False

    async def process_payment_webhook(self, payload: dict):
        """Process incoming BharatPe webhook notifications"""
        transaction_id = payload.get('transactionId')
        status = payload.get('status')
        amount = float(payload.get('amount', 0))
        
        payment = self.payment_repo.get_payment_by_transaction_id(transaction_id)
        if not payment:
            logger.error(f"Payment not found for transaction: {transaction_id}")
            return False
        
        if status == 'SUCCESS' and payment.amount == amount:
            self.payment_repo.update_payment_status(payment.id, 'completed')
            logger.info(f"Payment {transaction_id} marked as completed via webhook")
            return True
        
        logger.warning(f"Webhook verification failed for {transaction_id}")
        return False
