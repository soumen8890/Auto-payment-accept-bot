from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    if update.effective_message:
        text = "⚠️ An error occurred while processing your request. The admin has been notified."
        await update.effective_message.reply_text(text)
    
    # Notify admin
    if context.bot_data.get('admin_chat_id'):
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        
        message = (
            f"An exception was raised while handling an update\n"
            f"<pre>update = {html.escape(str(update))}</pre>\n\n"
            f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
            f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
            f"<pre>{html.escape(tb_string)}</pre>"
        )
        
        await context.bot.send_message(
            chat_id=context.bot_data['admin_chat_id'],
            text=message,
            parse_mode='HTML'
      )
