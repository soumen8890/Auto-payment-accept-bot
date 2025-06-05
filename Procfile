# Universal Procfile for Multi-Platform Deployment
# ----------------------------
# 1. Webhook Mode (Production)
web: &webhook
  if [ "$WEBHOOK_MODE" = "true" ]; then
    if [ -f "webhook.py" ]; then
      uvicorn webhook:app --host=0.0.0.0 --port=${PORT:-8000} --workers=${WORKERS:-2}
    else
      python bot.py --webhook
    fi
  else
    python bot.py --polling
  fi

# 2. Worker Mode (Background Tasks)
worker: &worker
  python worker.py || 
  (python -c "from services.subscription_service import SubscriptionService; SubscriptionService().run_background_tasks()")

# 3. Combined Mode (All-in-One)
combined: 
  command: *webhook &
  command: *worker

# Platform-Specific Variations
# ----------------------------
# Heroku
heroku_web: *webhook
heroku_worker: *worker

# Render
render_web: 
  sh -c "gunicorn -k uvicorn.workers.UvicornWorker -w ${WORKERS:-2} -b :${PORT:-8000} webhook:app"

# Railway
railway_web:
  python bot.py --webhook --port ${PORT}

# Koyeb
koyeb_web:
  if [ -z "$KOYEB_POSTGRES_URL" ]; then
    python bot.py --polling
  else
    python bot.py --webhook --port 8080
  fi

# VPS (Systemd)
vps_service: |
  [Unit]
  Description=Telegram Bot Service
  After=network.target
  [Service]
  User=ubuntu
  WorkingDirectory=/opt/your-bot
  ExecStart=/usr/bin/python3 bot.py --webhook --port 8000
  Restart=always
  [Install]
  WantedBy=multi-user.target
