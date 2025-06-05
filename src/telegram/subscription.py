from datetime import datetime, timedelta
from database.crud import get_user, update_user_subscription
from database.models import SubscriptionPlan

def add_subscription(user_id, plan_type, amount):
    user = get_user(user_id)
    
    if plan_type == "daily":
        expiry = datetime.now() + timedelta(days=1)
    elif plan_type == "monthly":
        expiry = datetime.now() + timedelta(days=30)
    elif plan_type == "yearly":
        expiry = datetime.now() + timedelta(days=365)
    elif plan_type == "lifetime":
        expiry = datetime.now() + timedelta(days=365*100)  # 100 years
    
    subscription = SubscriptionPlan(
        user_id=user_id,
        plan_type=plan_type,
        amount=amount,
        start_date=datetime.now(),
        expiry_date=expiry,
        is_active=True
    )
    
    update_user_subscription(user, subscription)
    return subscription
