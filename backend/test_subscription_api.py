#!/usr/bin/env python
"""
Test subscription API - check if user profile returns subscription info
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.users.models import User
from apps.users.serializers import UserSerializer

# Get a test user (the one with phone +99365532570)
user = User.objects(phone='+99365532570').first()

if not user:
    print("User not found!")
    sys.exit(1)

print(f"Testing UserSerializer for user: {user.phone}")
print(f"User ID: {user.id}")
print()

# Serialize user
serializer = UserSerializer(user)
data = serializer.data

print("Serialized data:")
print(f"- Phone: {data.get('phone')}")
print(f"- Name: {data.get('first_name')} {data.get('last_name')}")
print(f"- Subscription: {data.get('subscription')}")
print()

if data.get('subscription'):
    sub = data['subscription']
    print("Subscription details:")
    print(f"  - Plan: {sub.get('plan_name')}")
    print(f"  - Status: {sub.get('status')}")
    print(f"  - Start: {sub.get('start_date')}")
    print(f"  - End: {sub.get('end_date')}")
    print(f"  - Features: {sub.get('plan_features')}")
else:
    print("No active subscription found")

