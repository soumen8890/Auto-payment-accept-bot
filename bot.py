#!/usr/bin/env python3
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler,
    ContextTypes
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
from utils.logger import setup_logger

# Set up logging
logger = setup_logger(__name__)

# Define conversation states
PAYMENT, UTR_VERIFICATION, PAYTM_PAYMENT = range(3)

async def post_init(application: Application) -> None:
    """Initialize database and create tables"""
    logger.info("Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Schedule background jobs
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_expired_subscriptions,
        IntervalTrigger(hours=24),
        args=[application]
    )
    scheduler.add_job(
        send_subscription_reminders,
        IntervalTrigger(hours=12),
        args=[application]
    )
    scheduler.start()
    logger.info("Scheduled jobs started")

async def check_expired_subscriptions(app: Application) -> None:
    """Background job to check for expired subscriptions"""
    logger.info("Running expired subscriptions check...")
    db = next(get_db())
    try:
        subscription_service = SubscriptionService(db)
        await subscription_service.check_expired_subscriptions()
        logger.info("Completed expired subscriptions check")
    except Exception as e:
        logger.error(f"Error checking expired subscriptions: {str(e)}")
    finally:
        db.close()

async def send_subscription_reminders(app: Application) -> None:
    """Background job to send subscription renewal reminders"""
    logger.info("Sending subscription reminders...")
    db = next(get_db())
    try:
        from services.notification_service import NotificationService
        from database.repositories import SubscriptionRepository
        
        subscription_repo = SubscriptionRepository(db)
        notification_service = NotificationService()
        
        # Get subscriptions expiring in 3 days
        expiring_subs = subscription_repo.get_expiring_subscriptions(days=3)
        
        for sub in expiring_subs:
            days_left = (sub.end_date - datetime.now()).days
            await notification_service.send_subscription_reminder(
                sub.user.telegram_id,
                days_left
            )
        
        logger.info(f"Sent reminders to {len(expiring_subs)} users")
    except Exception as e:
        logger.error(f"Error sending reminders: {str(e)}")
    finally:
        db.close()

def setup_handlers(application: Application) -> None:
    """Configure all bot handlers"""
    db = next(get_db())
    
    # Initialize handlers
    payment_handlers = PaymentHandlers(db)
    subscription_handlers = SubscriptionHandlers(db)
    admin_handlers = AdminHandlers(db)
    user_handlers = UserHandlers(db)
    group_handlers = GroupHandlers(db)
    
    # Payment conversation handler
    payment_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('subscribe', payment_handlers.request_payment)],
        states={
            PAYMENT: [
                CallbackQueryHandler(payment_handlers.handle_payment_method, pattern='^payment_'),
                CallbackQueryHandler(payment_handlers.handle_plan_selection, pattern='^plan_')
            ],
            UTR_VERIFICATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, payment_handlers.handle_utr)
            ],
            PAYTM_PAYMENT: [
                CallbackQueryHandler(payment_handlers.handle_paytm_status, pattern='^paytm_')
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
    admin_filter = filters.User(user_id=settings.ADMIN_IDS)
    application.add_handler(CommandHandler(
        'stats', 
        admin_handlers.admin_stats, 
        filters=admin_filter
    ))
    application.add_handler(CommandHandler(
        'manage_user', 
        admin_handlers.manage_user, 
        filters=admin_filter
    ))
    
    # Group management
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        group_handlers.new_member
    ))
    application.add_handler(MessageHandler(
        filters.StatusUpdate.LEFT_CHAT_MEMBER,
        group_handlers.left_member
    ))
    
    # Add error handler
    application.add_error_handler(error_handler)

def main() -> None:
    """Run the bot"""
    # Create Application
    application = Application.builder() \
        .token(settings.BOT_TOKEN) \
        .post_init(post_init) \
        .build()
    
    # Set up handlers
    setup_handlers(application)
    
    # Run the bot
    logger.info("Starting bot...")
    if settings.WEBHOOK_MODE:
        from utils.helpers import get_ist_time
        webhook_url = f"{settings.WEBHOOK_URL}/{settings.BOT_TOKEN}"
        
        logger.info(f"Starting webhook at {webhook_url}")
        application.run_webhook(
            listen=settings.WEBHOOK_LISTEN,
            port=settings.WEBHOOK_PORT,
            url_path=settings.BOT_TOKEN,
            webhook_url=webhook_url,
            cert=settings.WEBHOOK_SSL_CERT if settings.WEBHOOK_SSL_CERT else None
        )
    else:
        logger.info("Starting in polling mode...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.critical(f"Bot crashed: {str(e)}", exc_info=True)
