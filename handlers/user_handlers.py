from telegram import Update
from telegram.ext import CallbackContext
from database.repositories import UserRepository

class UserHandlers:
    def __init__(self, db):
        self.db = db
        self.user_repo = UserRepository(db)

    async def start(self, update: Update, context: CallbackContext):
        user = update.effective_user
        existing_user = self.user_repo.get_by_telegram_id(user.id)
        
        if not existing_user:
            self.user_repo.create(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name
            )
        
        welcome_text = (
            "👋 Welcome to our premium membership bot!\n\n"
            "With this bot you can:\n"
            "• Subscribe to premium content\n"
            "• Get access to exclusive groups\n"
            "• Manage your subscription\n\n"
            "Use /subscribe to get started!"
        )
        
        await update.message.reply_text(welcome_text)

    async def help(self, update: Update, context: CallbackContext):
        help_text = (
            "🆘 Help Menu\n\n"
            "Available commands:\n"
            "/start - Welcome message\n"
            "/subscribe - Purchase a subscription\n"
            "/mysub - Check your subscription status\n"
            "/autorenew - Toggle auto-renewal\n"
            "/help - Show this message\n\n"
            "For payment issues, contact @admin"
        )
        await update.message.reply_text(help_text)

    async def profile(self, update: Update, context: CallbackContext):
        user = update.effective_user
        db_user = self.user_repo.get_by_telegram_id(user.id)
        
        profile_text = (
            f"👤 Your Profile\n\n"
            f"Username: @{db_user.username}\n"
            f"Name: {db_user.first_name} {db_user.last_name or ''}\n"
            f"Joined: {db_user.join_date.strftime('%Y-%m-%d')}\n"
            f"Status: {'Premium 🟢' if db_user.is_active else 'Basic 🔴'}"
        )
        
        await update.message.reply_text(profile_text)
