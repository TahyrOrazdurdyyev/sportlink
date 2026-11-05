#!/usr/bin/env python
"""
Create test categories
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.categories.models import Category

def create_categories():
    """Create test sport categories"""
    
    categories_data = [
        {
            'name_i18n': {
                'tk': 'Futbol',
                'ru': 'Футбол',
                'en': 'Football'
            },
            'description_i18n': {
                'tk': 'Futbol oýny',
                'ru': 'Игра в футбол',
                'en': 'Football game'
            }
        },
        {
            'name_i18n': {
                'tk': 'Tennis',
                'ru': 'Теннис',
                'en': 'Tennis'
            },
            'description_i18n': {
                'tk': 'Tennis oýny',
                'ru': 'Игра в теннис',
                'en': 'Tennis game'
            }
        },
        {
            'name_i18n': {
                'tk': 'Basketbol',
                'ru': 'Баскетбол',
                'en': 'Basketball'
            },
            'description_i18n': {
                'tk': 'Basketbol oýny',
                'ru': 'Игра в баскетбол',
                'en': 'Basketball game'
            }
        },
        {
            'name_i18n': {
                'tk': 'Woleýbol',
                'ru': 'Волейбол',
                'en': 'Volleyball'
            },
            'description_i18n': {
                'tk': 'Woleýbol oýny',
                'ru': 'Игра в волейбол',
                'en': 'Volleyball game'
            }
        },
        {
            'name_i18n': {
                'tk': 'Bedminton',
                'ru': 'Бадминтон',
                'en': 'Badminton'
            },
            'description_i18n': {
                'tk': 'Bedminton oýny',
                'ru': 'Игра в бадминтон',
                'en': 'Badminton game'
            }
        }
    ]
    
    print("Creating categories...")
    for data in categories_data:
        try:
            existing = Category.objects.filter(
                name_i18n__tk=data['name_i18n']['tk']
            ).first()
            
            if existing:
                print(f"⚠️  Category '{data['name_i18n']['tk']}' already exists")
            else:
                category = Category(**data)
                category.save()
                print(f"✅ Created: {data['name_i18n']['tk']} / {data['name_i18n']['ru']} / {data['name_i18n']['en']}")
        except Exception as e:
            print(f"❌ Error creating '{data['name_i18n']['tk']}': {e}")
    
    print(f"\n✅ Done! Total categories: {Category.objects.count()}")

if __name__ == '__main__':
    create_categories()

