# Subscription Plans
SUBSCRIPTION_PLANS = {
    'daily': {
        'duration_days': 1,
        'price': 50  # in INR
    },
    'monthly': {
        'duration_days': 30,
        'price': 500
    },
    'yearly': {
        'duration_days': 365,
        'price': 5000
    },
    'lifetime': {
        'duration_days': 3650,  # 10 years
        'price': 15000
    }
}

# Telegram Constants
MAX_GROUP_MEMBERS = 200000
MAX_CHANNEL_MEMBERS = 200000
ADMIN_PERMISSIONS = {
    'can_change_info': True,
    'can_post_messages': True,
    'can_edit_messages': True,
    'can_delete_messages': True,
    'can_invite_users': True,
    'can_restrict_members': True,
    'can_pin_messages': True,
    'can_promote_members': False
}

# Payment Status
PAYMENT_STATUS = {
    'PENDING': 0,
    'VERIFIED': 1,
    'FAILED': 2,
    'REFUNDED': 3
}
