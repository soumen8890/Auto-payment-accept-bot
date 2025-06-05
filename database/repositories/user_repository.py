from sqlalchemy.orm import Session
from database import models
from typing import Optional

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_telegram_id(self, telegram_id: int) -> Optional[models.User]:
        return self.db.query(models.User).filter(
            models.User.telegram_id == telegram_id
        ).first()
    
    def create(self, telegram_id: int, username: str, first_name: str) -> models.User:
        user = models.User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_active_status(self, telegram_id: int, is_active: bool) -> models.User:
        user = self.get_by_telegram_id(telegram_id)
        if user:
            user.is_active = is_active
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def get_active_users(self):
        return self.db.query(models.User).filter(
            models.User.is_active == True
        ).all()
