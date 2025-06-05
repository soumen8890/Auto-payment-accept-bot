# BharatPe UTR Verification & Paytm Automation Bot 🤖💸

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Telegram Bot](https://img.shields.io/badge/Telegram-Bot_API-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A robust subscription management Telegram bot with integrated BharatPe UTR verification and PayTM payment processing for premium group access.

## Key Features ✨

- **Automated Subscription Management**  
  - Daily/monthly/yearly/lifetime plans
  - Auto-renewal options
  - Expiration reminders

- **Payment Gateway Integration**  
  - BharatPe UTR verification
  - PayTM payment processing
  - Webhook support for instant notifications

- **Telegram Group Control**  
  - Automatic member onboarding
  - Subscription-based access
  - Graceful removal on expiration

- **Admin Dashboard**  
  - Real-time statistics
  - User management
  - Revenue tracking

## Tech Stack 🛠️

| Component          | Technology                |
|--------------------|---------------------------|
| Backend Framework  | Python 3.10+              |
| Telegram Library   | python-telegram-bot v20.x |
| Database           | PostgreSQL/SQLite         |
| Payment Gateways   | BharatPe API, PayTM API   |
| Scheduler          | APScheduler               |
| Web Framework      | FastAPI (for webhooks)    |

## Installation Guide 📥

### Prerequisites
- Python 3.10 or higher
- PostgreSQL (for production)
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/soumen8890/Auto-payment-accept-bot
   cd bharatpe-paytm-bot
