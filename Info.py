"""
System Information and Configuration Module
Contains metadata, version info, and platform configurations
"""

import os
from datetime import datetime
from typing import Dict, Any
from config import settings

class BotInfo:
    """Core system information and metadata"""
    
    # Basic Info
    NAME = "BharatPe PayTM Automation Bot"
    VERSION = "1.3.2"
    REPO = "https://github.com/yourusername/bharatpe-paytm-bot"
    LICENSE = "MIT"
    SUPPORT = "support@yourdomain.com"
    
    # System Metadata
    BUILD_DATE = datetime.utcnow().isoformat()
    PYTHON_VERSION = "3.10.6"
    TELEGRAM_BOT_API_VERSION = "20.3"
    
    # Payment System Capabilities
    PAYMENT_METHODS = {
        "bharatpe": {
            "min_amount": 10.00,
            "max_amount": 100000.00,
            "currency": "INR",
            "supported_banks": ["HDFC", "ICICI", "SBI", "AXIS"]
        },
        "paytm": {
            "min_amount": 1.00,
            "max_amount": 100000.00,
            "currency": "INR",
            "wallet_supported": True
        }
    }
    
    # Subscription Plans Configuration
    SUBSCRIPTION_PLANS = {
        "daily": {
            "price": 50.00,
            "duration_days": 1,
            "features": ["Basic group access"]
        },
        "monthly": {
            "price": 500.00,
            "duration_days": 30,
            "features": ["Premium content", "24/7 support"]
        },
        "lifetime": {
            "price": 15000.00,
            "duration_days": 3650,  # ~10 years
            "features": ["All premium features", "Priority support"]
        }
    }

    @classmethod
    def get_system_info(cls) -> Dict[str, Any]:
        """Return comprehensive system information"""
        return {
            "name": cls.NAME,
            "version": cls.VERSION,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database": {
                "connected": bool(settings.DB_URL),
                "type": "postgresql" if "postgres" in settings.DB_URL else "sqlite"
            },
            "payment_gateways": list(cls.PAYMENT_METHODS.keys()),
            "last_updated": cls.BUILD_DATE
        }

    @classmethod
    def get_telegram_commands(cls) -> list:
        """Generate Telegram Bot commands list for setMyCommands"""
        return [
            {
                "command": "start",
                "description": "Initialize the bot"
            },
            {
                "command": "subscribe",
                "description": "Purchase a subscription"
            },
            {
                "command": "mysub",
                "description": "Check subscription status"
            },
            {
                "command": "help",
                "description": "Show help information"
            }
        ]


class PlatformConfig:
    """Platform-specific deployment configurations"""
    
    HEROKU = {
        "web_port": os.getenv("PORT", 8000),
        "worker_enabled": True,
        "requires": ["heroku-postgresql"]
    }
    
    RENDER = {
        "web_port": 10000,
        "health_check_path": "/health",
        "build_command": "pip install -r requirements.txt"
    }
    
    DOCKER = {
        "exposed_ports": [8000],
        "volumes": ["/data"],
        "environment_vars": [
            "BOT_TOKEN",
            "DATABASE_URL",
            "WEBHOOK_MODE"
        ]
    }


def system_health_check() -> Dict[str, Any]:
    """Check critical system components"""
    from database.database import engine
    from services.bharatpe_service import BharatPeService
    
    checks = {
        "database": {
            "status": "ok",
            "latency": "0ms"
        },
        "payment_gateways": {},
        "telegram_api": {
            "status": "unknown"
        }
    }
    
    try:
        # Database check
        with engine.connect() as conn:
            start = datetime.now()
            conn.execute("SELECT 1")
            checks["database"]["latency"] = f"{(datetime.now() - start).microseconds/1000}ms"
    except Exception as e:
        checks["database"]["status"] = f"error: {str(e)}"
    
    # Payment gateway checks
    for gateway in ["bharatpe", "paytm"]:
        try:
            if gateway == "bharatpe":
                BharatPeService().verify_utr("TEST", 1.00)
                checks["payment_gateways"][gateway] = {"status": "ok"}
        except Exception as e:
            checks["payment_gateways"][gateway] = {"status": f"error: {str(e)}"}
    
    return checks


if __name__ == "__main__":
    print("=== System Information ===")
    print(BotInfo.get_system_info())
    print("\n=== Health Check ===")
    print(system_health_check())
