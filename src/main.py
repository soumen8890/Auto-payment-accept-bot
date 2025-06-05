from telegram.bot import start_bot
from utils.scheduler import start_scheduler
from database.database import init_db

def main():
    # Initialize database
    init_db()
    
    # Start subscription check scheduler
    start_scheduler()
    
    # Start Telegram bot
    start_bot()

if __name__ == "__main__":
    main()
