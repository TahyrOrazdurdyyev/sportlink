#!/usr/bin/env python
"""
Create test subscription for user
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.users.models import User
from apps.subscriptions.models import SubscriptionPlan
from apps.subscriptions.models_user import UserSubscription
from datetime import datetime, timedelta

# Get user
user = User.objects(phone='+99365532570').first()
if not user:
    print("User not found!")
    sys.exit(1)

# Get Sport+ plan
plan = SubscriptionPlan.objects(id='43f0823a-0d8e-4979-96ce-772332f68a26').first()
if not plan:
    print("Plan not found!")
    sys.exit(1)

# Cancel any existing active subscriptions
existing = UserSubscription.objects(user=user, status='active').first()
if existing:
    print(f"Cancelling existing subscription: {existing.id}")
    existing.cancel()

# Create new subscription (30 days)
start_date = datetime.utcnow()
end_date = start_date + timedelta(days=30)

subscription = UserSubscription(
    user=user,
    plan=plan,
    start_date=start_date,
    end_date=end_date,
    status='active',
    amount_paid=plan.monthly_price,
    payment_method='manual',
    transaction_id=f'TEST_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}',
)
subscription.save()

print(f"✅ Created subscription for {user.phone}")
print(f"   Plan: {plan.name}")
print(f"   Start: {start_date}")
print(f"   End: {end_date}")
print(f"   Status: {subscription.status}")
print(f"   ID: {subscription.id}")

