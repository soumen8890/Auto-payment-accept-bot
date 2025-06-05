from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import models
from typing import List, Optional

class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_active_subscription(self, user_id: int) -> Optional[models.Subscription]:
        return self.db.query(models.Subscription).filter(
            models.Subscription.user_id == user_id,
            models.Subscription.is_active == True,
            models.Subscription.end_date > datetime.now()
        ).first()
    
    def create_subscription(
        self,
        user_id: int,
        plan_id: int,
        duration_days: int
    ) -> models.Subscription:
        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration_days)
        
        subscription = models.Subscription(
            user_id=user_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date
        )
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
    
    def get_expired_subscriptions(self) -> List[models.Subscription]:
        return self.db.query(models.Subscription).filter(
            models.Subscription.is_active == True,
            models.Subscription.end_date <= datetime.now()
        ).all()
    
    def deactivate_subscription(self, subscription_id: int) -> None:
        subscription = self.db.query(models.Subscription).get(subscription_id)
        if subscription:
            subscription.is_active = False
            self.db.commit()
