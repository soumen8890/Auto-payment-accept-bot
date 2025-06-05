from sqlalchemy.orm import Session
from database import models

def get_user(db: Session, telegram_id: int):
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()

def create_user(db: Session, telegram_id: int, username: str, first_name: str):
    db_user = models.User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_subscription(db: Session, user_id: int, plan_id: int, end_date):
    db_subscription = models.Subscription(
        user_id=user_id,
        plan_id=plan_id,
        end_date=end_date
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

# Additional CRUD operations for payments, plans, etc.
