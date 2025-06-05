from datetime import datetime, timedelta
from typing import Dict, List
from database.repositories import (
    UserRepository,
    SubscriptionRepository,
    PaymentRepository
)
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db):
        self.db = db
        self.user_repo = UserRepository(db)
        self.subscription_repo = SubscriptionRepository(db)
        self.payment_repo = PaymentRepository(db)

    def get_daily_signups(self, days: int = 30) -> Dict[str, int]:
        """Get daily user signups for the last N days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        results = self.user_repo.get_signups_by_date(start_date, end_date)
        return {str(date): count for date, count in results}

    def get_revenue_stats(self, period: str = 'monthly') -> Dict[str, float]:
        """Get revenue statistics for the given period"""
        if period == 'daily':
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
        elif period == 'weekly':
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=1)
        else:  # monthly
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        
        return self.payment_repo.get_revenue_by_period(start_date, end_date)

    def get_subscription_metrics(self) -> Dict[str, float]:
        """Get key subscription metrics"""
        metrics = {
            'total_users': self.user_repo.count_users(),
            'active_subscriptions': self.subscription_repo.count_active_subscriptions(),
            'renewal_rate': self.subscription_repo.calculate_renewal_rate(),
            'avg_subscription_length': self.subscription_repo.avg_subscription_duration()
        }
        return metrics

    def get_plan_distribution(self) -> Dict[str, float]:
        """Get distribution of subscription plans"""
        return self.subscription_repo.get_plan_distribution()
