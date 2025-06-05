from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True)
    username = Column(String)
    join_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

class SubscriptionPlan(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    plan_type = Column(String)  # daily, monthly, yearly, lifetime
    amount = Column(Float)
    start_date = Column(DateTime)
    expiry_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
