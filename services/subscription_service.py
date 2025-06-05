from datetime import datetime, timedelta
import logging
from typing import Optional
from database.repositories import SubscriptionRepository, UserRepository
from services.telegram_service import TelegramService
from config import settings

logger = logging.getLogger(__name__)

class SubscriptionService:
    def __init__(self, db):
        self.db = db
        self.subscription_repo = SubscriptionRepository(db)
        self.user_repo = UserRepository(db)
        self.telegram_service = TelegramService(settings.BOT_TOKEN)

    async def create_subscription(self, user_id: int, plan_name: str) -> bool:
        """Create new subscription for user"""
        plan = settings.SUBSCRIPTION_PLANS.get(plan_name)
        if not plan:
            logger.error(f"Invalid plan name: {plan_name}")
            return False
            
        end_date = datetime.now() + timedelta(days=plan['duration_days'])
        
        try:
            # Create subscription record
            subscription = self.subscription_repo.create_subscription(
                user_id=user_id,
                plan_id=plan_name,
                duration_days=plan['duration_days']
            )
            
            # Update user status
            self.user_repo.update_active_status(user_id, True)
            
            # Add to premium group
            await self.telegram_service.add_to_group(user_id)
            await self.telegram_service.add_to_channel(user_id)
            
            logger.info(f"Created {plan_name} subscription for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create subscription: {str(e)}")
            return False

    async def renew_subscription(self, user_id: int, plan_name: str) -> bool:
        """Renew existing subscription"""
        current_sub = self.subscription_repo.get_active_subscription(user_id)
        plan = settings.SUBSCRIPTION_PLANS.get(plan_name)
        
        if not plan:
            logger.error(f"Invalid plan name: {plan_name}")
            return False
            
        if current_sub:
            new_end_date = max(
                current_sub.end_date,
                datetime.now()
            ) + timedelta(days=plan['duration_days'])
        else:
            new_end_date = datetime.now() + timedelta(days=plan['duration_days'])
        
        try:
            if current_sub:
                self.subscription_repo.update_end_date(
                    current_sub.id,
                    new_end_date
                )
            else:
                self.subscription_repo.create_subscription(
                    user_id=user_id,
                    plan_id=plan_name,
                    duration_days=plan['duration_days']
                )
            
            self.user_repo.update_active_status(user_id, True)
            logger.info(f"Renewed {plan_name} subscription for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to renew subscription: {str(e)}")
            return False

    async def check_expired_subscriptions(self):
        """Check and process expired subscriptions"""
        expired_subs = self.subscription_repo.get_expired_subscriptions()
        
        for subscription in expired_subs:
            try:
                # Deactivate subscription
                self.subscription_repo.deactivate_subscription(subscription.id)
                
                # Update user status
                self.user_repo.update_active_status(subscription.user_id, False)
                
                # Remove from premium group
                await self.telegram_service.remove_from_group(subscription.user_id)
                
                # Notify user
                await self.telegram_service.send_message_to_user(
                    subscription.user_id,
                    "⚠️ Your subscription has expired. Use /subscribe to renew."
                )
                
                logger.info(f"Processed expired subscription for user {subscription.user_id}")
                
            except Exception as e:
                logger.error(f"Failed to process expired subscription {subscription.id}: {str(e)}")
