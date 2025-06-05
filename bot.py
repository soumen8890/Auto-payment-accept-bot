import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler
)
from config import settings
from database.database import get_db, Base, engine
from handlers import (
    PaymentHandlers,
    SubscriptionHandlers,
    AdminHandlers,
    UserHandlers,
    GroupHandlers,
    error_handler
)
from services.subscription_service import SubscriptionService
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
PAYMENT, UTR_VERIFICATION = range(2)

async def post_init(application: Application):
    """Initialize database and create tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Schedule background jobs
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_expired_subscriptions,
        IntervalTrigger(hours=24),
        args=[application]
    )
    scheduler.start()
    logger.info("Scheduled jobs started")

async def check_expired_subscriptions(app: Application):
    """Background job to check for expired subscriptions"""
    db = next(get_db())
    try:
        subscription_service = SubscriptionService(db)
        await subscription_service.check_expired_subscriptions()
        logger.info("Completed expired subscriptions check")
    except Exception as e:
        logger.error(f"Error checking expired subscriptions: {str(e)}")
    finally:
        db.close()

def main():
    # Initialize database session
    db = next(get_db())
    
    # Initialize handlers
    payment_handlers = PaymentHandlers(db)
    subscription_handlers = SubscriptionHandlers(db)
    admin_handlers = AdminHandlers(db)
    user_handlers = UserHandlers(db)
    group_handlers = GroupHandlers(db)
    
    # Create Application
    application = Application.builder() \
        .token(settings.BOT_TOKEN) \
        .post_init(post_init) \
        .build()
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Conversation handler for payment flow
    payment_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('subscribe', payment_handlers.request_payment)],
        states={
            PAYMENT: [
                CallbackQueryHandler(payment_handlers.handle_payment_method, pattern='^payment_'),
                CallbackQueryHandler(payment_handlers.handle_plan_selection, pattern='^plan_')
            ],
            UTR_VERIFICATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, payment_handlers.handle_utr)
            ]
        },
        fallbacks=[CommandHandler('cancel', user_handlers.cancel_conversation)],
        allow_reentry=True
    )
    
    # Add handlers
    application.add_handler(payment_conv_handler)
    application.add_handler(CommandHandler('start', user_handlers.start))
    application.add_handler(CommandHandler('help', user_handlers.help))
    application.add_handler(CommandHandler('profile', user_handlers.profile))
    application.add_handler(CommandHandler('mysub', subscription_handlers.check_subscription))
    application.add_handler(CommandHandler('autorenew', subscription_handlers.toggle_auto_renew))
    
    # Admin commands
    application.add_handler(CommandHandler('stats', admin_handlers.admin_stats))
    application.add_handler(CommandHandler('manage_user', admin_handlers.manage_user))
    
    # Group handlers
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        group_handlers.new_member
    ))
    application.add_handler(MessageHandler(
        filters.StatusUpdate.LEFT_CHAT_MEMBER,
        group_handlers.left_member
    ))
    
    # Run the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
