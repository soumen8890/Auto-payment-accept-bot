from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime, timedelta
from database.repositories import SubscriptionRepository, UserRepository
from services.telegram_service import add_to_group
from config import settings

class SubscriptionHandlers:
    def __init__(self, db):
        self.db = db
        self.subscription_repo = SubscriptionRepository(db)
        self.user_repo = UserRepository(db)

    async def check_subscription(self, update: Update, context: CallbackContext):
        user = update.effective_user
        subscription = self.subscription_repo.get_active_subscription(user.id)
        
        if subscription:
            days_left = (subscription.end_date - datetime.now()).days
            await update.message.reply_text(
                f"Your subscription is active until {subscription.end_date.strftime('%Y-%m-%d')}\n"
                f"Days remaining: {days_left}"
            )
        else:
            await update.message.reply_text(
                "You don't have an active subscription. Use /subscribe to get started."
            )

    async def renew_subscription(self, update: Update, context: CallbackContext):
        user = update.effective_user
        subscription = self.subscription_repo.get_active_subscription(user.id)
        
        if subscription and subscription.auto_renew:
            await update.message.reply_text(
                "Your subscription is set to auto-renew. "
                "To change this, use /autorenew"
            )
        else:
            await update.message.reply_text(
                "Please use /subscribe to renew your subscription."
            )

    async def toggle_auto_renew(self, update: Update, context: CallbackContext):
        user = update.effective_user
        subscription = self.subscription_repo.get_active_subscription(user.id)
        
        if not subscription:
            await update.message.reply_text(
                "You don't have an active subscription. Use /subscribe first."
            )
            return
        
        new_status = not subscription.auto_renew
        subscription.auto_renew = new_status
        self.db.commit()
        
        await update.message.reply_text(
            f"Auto-renew has been {'enabled' if new_status else 'disabled'} for your subscription."
        )

    async def process_expired_subscriptions(self):
        expired_subs = self.subscription_repo.get_expired_subscriptions()
        for subscription in expired_subs:
            self.subscription_repo.deactivate_subscription(subscription.id)
            self.user_repo.update_active_status(subscription.user_id, False)
            
            # Remove from premium group (implementation depends on your Telegram service)
            await remove_from_group(subscription.user_id)
