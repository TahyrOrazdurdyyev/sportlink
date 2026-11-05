#!/usr/bin/env python
"""
Add test tariffs to courts
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.courts.models import Court, Tariff
from decimal import Decimal

def add_tariffs():
    """Add tariffs to existing courts"""
    
    courts = Court.objects.all()
    
    if courts.count() == 0:
        print("❌ No courts found. Please create courts first.")
        return
    
    print(f"Found {courts.count()} courts. Adding tariffs...\n")
    
    for court in courts:
        if court.tariffs and len(court.tariffs) > 0:
            print(f"⚠️  {court.get_name('tk')} already has tariffs, skipping...")
            continue
        
        # Standard tariff
        standard_tariff = Tariff(
            name_i18n={
                'tk': 'Adaty nyrh',
                'ru': 'Стандартный тариф',
                'en': 'Standard Rate'
            },
            description_i18n={
                'tk': 'Gündizki sagatlar üçin',
                'ru': 'Для дневных часов',
                'en': 'For daytime hours'
            },
            base_price=Decimal('50.00'),
            price_type='per_hour',
            min_booking_hours=1,
            max_booking_hours=3
        )
        
        # Premium tariff
        premium_tariff = Tariff(
            name_i18n={
                'tk': 'Ýokary hilli nyrh',
                'ru': 'Премиум тариф',
                'en': 'Premium Rate'
            },
            description_i18n={
                'tk': 'Agşamky sagatlar üçin',
                'ru': 'Для вечерних часов',
                'en': 'For evening hours'
            },
            base_price=Decimal('80.00'),
            price_type='per_hour',
            min_booking_hours=1,
            max_booking_hours=3
        )
        
        # Weekend tariff
        weekend_tariff = Tariff(
            name_i18n={
                'tk': 'Dynç günleri',
                'ru': 'Выходные дни',
                'en': 'Weekend Rate'
            },
            description_i18n={
                'tk': 'Şenbe we ýekşenbe',
                'ru': 'Суббота и воскресенье',
                'en': 'Saturday and Sunday'
            },
            base_price=Decimal('100.00'),
            price_type='per_hour',
            min_booking_hours=2,
            max_booking_hours=4
        )
        
        court.tariffs = [standard_tariff, premium_tariff, weekend_tariff]
        court.save()
        
        print(f"✅ Added 3 tariffs to: {court.get_name('tk')} ({court.type})")
    
    print(f"\n✅ Done!")

if __name__ == '__main__':
    add_tariffs()

