#!/usr/bin/env python
"""
Create admin user for Sportlink
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.users.models import User

def create_admin():
    phone = "+99365000000"  # Admin phone
    email = "admin@sportlink.tm"
    password = "admin123"
    
    # Check if admin exists
    try:
        user = User.objects.get(phone=phone)
        print(f"❌ Admin already exists: {user}")
        print(f"   Phone: {phone}")
        print(f"   Email: {user.email}")
        return
    except User.DoesNotExist:
        pass
    
    # Create admin
    admin = User(
        phone=phone,
        email=email,
        first_name="Admin",
        last_name="User",
        is_staff=True,
        is_superuser=True,
        is_active=True,
    )
    admin.set_password(password)
    admin.save()
    
    print("✅ Admin user created successfully!")
    print(f"   Phone: {phone}")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"\n   You can now login at http://localhost:3000/login")

if __name__ == '__main__':
    create_admin()

