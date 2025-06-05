import logging
import sys
from logging.handlers import RotatingFileHandler
from config import settings

def setup_logger(name: str) -> logging.Logger:
    """Configure and return a logger with file and console output"""
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    
    # Formatting
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (rotating)
    file_handler = RotatingFileHandler(
        'bot.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

class TelegramLogsHandler(logging.Handler):
    """Custom handler to send critical logs to Telegram admin"""
    def __init__(self, telegram_service):
        super().__init__()
        self.telegram_service = telegram_service
        self.setLevel(logging.ERROR)
    
    def emit(self, record):
        log_entry = self.format(record)
        self.telegram_service.send_message_to_admin(f"🚨 ERROR: {log_entry}")
