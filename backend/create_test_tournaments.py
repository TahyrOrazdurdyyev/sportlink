#!/usr/bin/env python
"""
Create test tournaments
"""
import os
import sys
import django
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.tournaments.models import Tournament
from apps.users.models import User
from decimal import Decimal

def create_tournaments():
    """Create test tournaments"""
    
    # Get admin user
    try:
        admin = User.objects.get(email='admin@sportlink.tm')
    except User.DoesNotExist:
        print("❌ Admin user not found. Please create admin first.")
        return
    
    today = datetime.utcnow()
    
    tournaments_data = [
        {
            'name_i18n': {
                'tk': 'Ýaz tennis ýaryşy',
                'ru': 'Весенний теннисный турнир',
                'en': 'Spring Tennis Tournament'
            },
            'description_i18n': {
                'tk': 'Ýaşlar üçin tennis ýaryşy',
                'ru': 'Теннисный турнир для молодежи',
                'en': 'Tennis tournament for youth'
            },
            'start_date': today + timedelta(days=30),
            'end_date': today + timedelta(days=32),
            'registration_deadline': today + timedelta(days=25),
            'max_participants': 32,
            'min_participants': 16,
            'registration_fee': Decimal('50.00'),
            'registration_open': True,
            'status': 'open',
            'created_by': admin
        },
        {
            'name_i18n': {
                'tk': 'Futbol çempionaty',
                'ru': 'Футбольный чемпионат',
                'en': 'Football Championship'
            },
            'description_i18n': {
                'tk': 'Toparlaýyn futbol çempionaty',
                'ru': 'Командный футбольный чемпионат',
                'en': 'Team football championship'
            },
            'start_date': today + timedelta(days=45),
            'end_date': today + timedelta(days=60),
            'registration_deadline': today + timedelta(days=40),
            'max_participants': 16,
            'min_participants': 8,
            'registration_fee': Decimal('100.00'),
            'registration_open': True,
            'status': 'open',
            'created_by': admin
        },
        {
            'name_i18n': {
                'tk': 'Basketbol kubogy',
                'ru': 'Кубок по баскетболу',
                'en': 'Basketball Cup'
            },
            'description_i18n': {
                'tk': 'Halk arasynda basketbol ýaryşy',
                'ru': 'Любительский турнир по баскетболу',
                'en': 'Amateur basketball tournament'
            },
            'start_date': today + timedelta(days=20),
            'end_date': today + timedelta(days=21),
            'registration_deadline': today + timedelta(days=15),
            'max_participants': 24,
            'min_participants': 12,
            'registration_fee': Decimal('0.00'),
            'registration_open': True,
            'status': 'open',
            'created_by': admin
        }
    ]
    
    print("Creating tournaments...\n")
    for data in tournaments_data:
        try:
            existing = Tournament.objects.filter(
                name_i18n__tk=data['name_i18n']['tk']
            ).first()
            
            if existing:
                print(f"⚠️  Tournament '{data['name_i18n']['tk']}' already exists")
            else:
                tournament = Tournament(**data)
                tournament.save()
                print(f"✅ Created: {data['name_i18n']['tk']}")
                print(f"   Dates: {data['start_date'].strftime('%Y-%m-%d')} - {data['end_date'].strftime('%Y-%m-%d')}")
                print(f"   Participants: {data['max_participants']}, Fee: {data['registration_fee']} TMT")
        except Exception as e:
            print(f"❌ Error creating '{data['name_i18n']['tk']}': {e}")
    
    print(f"\n✅ Done! Total tournaments: {Tournament.objects.count()}")

if __name__ == '__main__':
    create_tournaments()

