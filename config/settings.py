import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Telegram Configuration
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    OWNER_ID = int(os.getenv('OWNER_ID'))
    
    # Database Configuration
    DB_URL = os.getenv('DB_URL', 'sqlite:///database.db')
    
    # Group/Channel IDs
    GROUP_ID = int(os.getenv('GROUP_ID', 0))
    CHANNEL_ID = int(os.getenv('CHANNEL_ID', 0))
    
    # Payment Verification
    PAYMENT_VERIFICATION_TIMEOUT = int(os.getenv('PAYMENT_VERIFICATION_TIMEOUT', 3600))  # 1 hour
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def DATABASE_CONFIG(self):
        return {
            'connections': {
                'default': self.DB_URL
            },
            'apps': {
                'models': {
                    'models': ['database.models', 'aerich.models'],
                    'default_connection': 'default',
                }
            }
        }

settings = Settings()
