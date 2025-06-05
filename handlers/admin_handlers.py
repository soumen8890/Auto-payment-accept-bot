from telegram import Update
from telegram.ext import CallbackContext
from database.repositories import UserRepository, SubscriptionRepository

class AdminHandlers:
    def __init__(self, db):
        self.db = db
        self.user_repo = UserRepository(db)
        self.subscription_repo = SubscriptionRepository(db)

    async def admin_stats(self, update: Update, context: CallbackContext):
        if not await self._is_admin(update.effective_user.id):
            await update.message.reply_text("You are not authorized to use this command.")
            return
        
        total_users = self.user_repo.count_users()
        active_users = self.user_repo.count_active_users()
        revenue = self.subscription_repo.get_total_revenue()
        
        await update.message.reply_text(
            f"📊 Admin Statistics:\n\n"
            f"👥 Total Users: {total_users}\n"
            f"🟢 Active Subscriptions: {active_users}\n"
            f"💰 Total Revenue: {revenue:.2f}"
        )

    async def manage_user(self, update: Update, context: CallbackContext):
        if not await self._is_admin(update.effective_user.id):
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /manage_user <user_id> <action>")
            return
        
        user_id = int(context.args[0])
        action = context.args[1].lower()
        
        if action == "ban":
            self.user_repo.ban_user(user_id)
            await update.message.reply_text(f"User {user_id} has been banned.")
        elif action == "unban":
            self.user_repo.unban_user(user_id)
            await update.message.reply_text(f"User {user_id} has been unbanned.")
        elif action == "add_sub":
            if len(context.args) < 3:
                await update.message.reply_text("Usage: /manage_user <user_id> add_sub <days>")
                return
            days = int(context.args[2])
            self.subscription_repo.add_days_to_subscription(user_id, days)
            await update.message.reply_text(f"Added {days} days to user {user_id}'s subscription.")
        else:
            await update.message.reply_text("Invalid action. Available actions: ban, unban, add_sub")

    async def _is_admin(self, user_id: int) -> bool:
        user = self.user_repo.get_by_telegram_id(user_id)
        return user and user.is_admin
