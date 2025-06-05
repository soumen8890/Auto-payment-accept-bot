from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.sql import func
from database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    join_date = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    duration_days = Column(Integer)
    price = Column(Float)
    description = Column(String(255), nullable=True)

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"))
    start_date = Column(DateTime, server_default=func.now())
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    auto_renew = Column(Boolean, default=False)

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    amount = Column(Float)
    payment_method = Column(String(50))  # 'bharatpe', 'paytm', etc.
    transaction_id = Column(String(100), unique=True)  # UTR for BharatPe
    status = Column(String(20), default="pending")  # pending, completed, failed
    payment_date = Column(DateTime, server_default=func.now())
    verification_date = Column(DateTime, nullable=True)
