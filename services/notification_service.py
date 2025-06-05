from typing import List
from services.telegram_service import TelegramService
from config import settings
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.telegram_service = TelegramService(settings.BOT_TOKEN)

    async def send_subscription_reminder(self, user_id: int, days_left: int):
        """Send subscription expiration reminder"""
        message = (
            f"🔔 Reminder: Your subscription will expire in {days_left} days.\n\n"
            "Renew now to avoid interruption of service.\n"
            "Use /subscribe to renew."
        )
        
        await self.telegram_service.send_message_to_user(user_id, message)
        logger.info(f"Sent reminder to user {user_id} ({days_left} days left)")

    async def send_payment_receipt(self, user_id: int, amount: float, plan_name: str):
        """Send payment confirmation receipt"""
        message = (
            f"🧾 Payment Receipt\n\n"
            f"Plan: {plan_name.capitalize()}\n"
            f"Amount: ₹{amount:.2f}\n"
            f"Status: Completed\n\n"
            "Thank you for your payment!"
        )
        
        await self.telegram_service.send_message_to_user(user_id, message)
        logger.info(f"Sent receipt to user {user_id} for {plan_name} subscription")

    async def notify_admin(self, message: str):
        """Send notification to admin"""
        if settings.ADMIN_CHAT_ID:
            await self.telegram_service.send_message_to_user(
                settings.ADMIN_CHAT_ID,
                message
      )
