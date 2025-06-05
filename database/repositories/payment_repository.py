from sqlalchemy.orm import Session
from database import models
from typing import Optional

class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_payment(
        self,
        subscription_id: int,
        amount: float,
        payment_method: str,
        transaction_id: str
    ) -> models.Payment:
        payment = models.Payment(
            subscription_id=subscription_id,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment
    
    def get_payment_by_transaction_id(self, transaction_id: str) -> Optional[models.Payment]:
        return self.db.query(models.Payment).filter(
            models.Payment.transaction_id == transaction_id
        ).first()
    
    def update_payment_status(
        self,
        payment_id: int,
        status: str
    ) -> models.Payment:
        payment = self.db.query(models.Payment).get(payment_id)
        if payment:
            payment.status = status
            payment.verification_date = datetime.now()
            self.db.commit()
            self.db.refresh(payment)
        return payment
