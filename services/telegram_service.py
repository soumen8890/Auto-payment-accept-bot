from telegram import Bot, ChatPermissions
from telegram.error import TelegramError
import logging
from config import settings
from typing import Optional, List

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, bot_token: str):
        self.bot = Bot(token=bot_token)
        self.group_id = settings.GROUP_ID
        self.channel_id = settings.CHANNEL_ID

    async def add_to_group(self, user_id: int) -> bool:
        """Add user to premium group"""
        try:
            await self.bot.restrict_chat_member(
                chat_id=self.group_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False
                )
            )
            await self.bot.send_message(
                chat_id=user_id,
                text="🎉 You've been added to the premium group! "
                     "Check your Telegram chats."
            )
            return True
        except TelegramError as e:
            logger.error(f"Failed to add user {user_id} to group: {str(e)}")
            return False

    async def remove_from_group(self, user_id: int) -> bool:
        """Remove user from premium group"""
        try:
            await self.bot.ban_chat_member(
                chat_id=self.group_id,
                user_id=user_id,
                until_date=60  # Ban for 60 seconds (soft remove)
            )
            await self.bot.send_message(
                chat_id=user_id,
                text="⚠️ Your access to the premium group has ended. "
                     "Renew your subscription with /subscribe to regain access."
            )
            return True
        except TelegramError as e:
            logger.error(f"Failed to remove user {user_id} from group: {str(e)}")
            return False

    async def add_to_channel(self, user_id: int) -> bool:
        """Add user to premium channel"""
        try:
            await self.bot.restrict_chat_member(
                chat_id=self.channel_id,
                user_id=user_id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False
                )
            )
            return True
        except TelegramError as e:
            logger.error(f"Failed to add user {user_id} to channel: {str(e)}")
            return False

    async def send_message_to_user(self, user_id: int, text: str) -> bool:
        """Send direct message to user"""
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=text
            )
            return True
        except TelegramError as e:
            logger.error(f"Failed to send message to user {user_id}: {str(e)}")
            return False
