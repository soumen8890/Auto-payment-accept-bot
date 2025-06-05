from functools import wraps
from typing import Callable, Any
import time
from utils.logger import setup_logger

logger = setup_logger(__name__)

def retry(max_attempts: int = 3, delay: int = 1):
    """Decorator to retry a function on failure"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt} failed for {func.__name__}: {str(e)}"
                    )
                    if attempt < max_attempts:
                        time.sleep(delay)
            
            logger.error(
                f"All {max_attempts} attempts failed for {func.__name__}"
            )
            raise last_exception
        return wrapper
    return decorator

def admin_only(func: Callable) -> Callable:
    """Restrict command to admin users only"""
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        from database.repositories import UserRepository
        from database.database import get_db
        
        db = next(get_db())
        try:
            user_repo = UserRepository(db)
            user = user_repo.get_by_telegram_id(update.effective_user.id)
            
            if user and user.is_admin:
                return await func(update, context, *args, **kwargs)
            else:
                await update.message.reply_text(
                    "⛔ This command is restricted to admins only."
                )
        finally:
            db.close()
    return wrapper

def db_session(func: Callable) -> Callable:
    """Provide database session to function and handle cleanup"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        from database.database import get_db
        
        db = next(get_db())
        try:
            kwargs['db'] = db
            return await func(*args, **kwargs)
        finally:
            db.close()
    return wrapper
