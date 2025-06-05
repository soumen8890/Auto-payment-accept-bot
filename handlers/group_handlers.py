from telegram import Update
from telegram.ext import CallbackContext
from database.repositories import UserRepository
from services.telegram_service import add_to_group, remove_from_group
from config import settings

class GroupHandlers:
    def __init__(self, db):
        self.db = db
        self.user_repo = UserRepository(db)

    async def new_member(self, update: Update, context: CallbackContext):
        for new_member in update.message.new_chat_members:
            user = self.user_repo.get_by_telegram_id(new_member.id)
            
            if user and user.is_active:
                # User has active subscription, allow to stay
                continue
            else:
                # Remove user if no active subscription
                await remove_from_group(new_member.id)
                await context.bot.send_message(
                    chat_id=new_member.id,
                    text="You need an active subscription to join this group. "
                         "Please use /subscribe to get access."
                )

    async def left_member(self, update: Update, context: CallbackContext):
        left_member = update.message.left_chat_member
        # You might want to log this or perform cleanup
        pass

    async def group_message(self, update: Update, context: CallbackContext):
        # Handle group messages if needed
        pass
