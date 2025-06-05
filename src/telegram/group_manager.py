from telethon import TelegramClient
from config.config import API_ID, API_HASH
from database.crud import get_active_subscribers

async def add_to_groups(client, user_id):
    groups = ["group1", "group2"]  # Your group usernames
    for group in groups:
        try:
            await client.add_user_to_group(user_id, group)
        except Exception as e:
            print(f"Error adding user to group {group}: {e}")

async def remove_from_groups(client, user_id):
    groups = ["group1", "group2"]  # Your group usernames
    for group in groups:
        try:
            await client.remove_user_from_group(user_id, group)
        except Exception as e:
            print(f"Error removing user from group {group}: {e}")
