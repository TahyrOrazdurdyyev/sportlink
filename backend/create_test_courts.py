#!/usr/bin/env python
"""
Create test courts
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.courts.models import Court

def create_courts():
    """Create test courts in Ashgabat"""
    
    courts_data = [
        {
            'name_i18n': {
                'tk': 'Merkezi tennis korty',
                'ru': 'Центральный теннисный корт',
                'en': 'Central Tennis Court'
            },
            'address': 'Saparmyrat Türkmenbaşy şaýoly 108, Aşgabat',
            'location': {
                'type': 'Point',
                'coordinates': [58.3794, 37.9601]  # Ashgabat coordinates
            },
            'type': 'tennis',
            'is_active': True,
            'attributes': {
                'surface': 'hard',
                'lights': True,
                'indoor': False,
                'capacity': 2
            },
            'images': []
        },
        {
            'name_i18n': {
                'tk': 'Olimpiýa futbol meýdançasy',
                'ru': 'Олимпийское футбольное поле',
                'en': 'Olympic Football Field'
            },
            'address': 'Olimpiýa şäherçesi, Aşgabat',
            'location': {
                'type': 'Point',
                'coordinates': [58.3264, 37.9398]
            },
            'type': 'football',
            'is_active': True,
            'attributes': {
                'surface': 'grass',
                'lights': True,
                'indoor': False,
                'capacity': 22
            },
            'images': []
        },
        {
            'name_i18n': {
                'tk': 'Sport sport basketbol zalы',
                'ru': 'Спортивный баскетбольный зал',
                'en': 'Sports Basketball Hall'
            },
            'address': 'Atamyrat Nyýazow şaýoly 145, Aşgabat',
            'location': {
                'type': 'Point',
                'coordinates': [58.3450, 37.9200]
            },
            'type': 'basketball',
            'is_active': True,
            'attributes': {
                'surface': 'parquet',
                'lights': True,
                'indoor': True,
                'capacity': 10
            },
            'images': []
        },
        {
            'name_i18n': {
                'tk': 'Bedminton klubi',
                'ru': 'Бадминтонный клуб',
                'en': 'Badminton Club'
            },
            'address': 'Görogly köçesi 56, Aşgabat',
            'location': {
                'type': 'Point',
                'coordinates': [58.3950, 37.9450]
            },
            'type': 'other',
            'is_active': True,
            'attributes': {
                'surface': 'synthetic',
                'lights': True,
                'indoor': True,
                'capacity': 4
            },
            'images': []
        },
        {
            'name_i18n': {
                'tk': 'Woleýbol meýdançasy',
                'ru': 'Волейбольная площадка',
                'en': 'Volleyball Court'
            },
            'address': 'Magtymguly şaýoly 92, Aşgabat',
            'location': {
                'type': 'Point',
                'coordinates': [58.3600, 37.9300]
            },
            'type': 'volleyball',
            'is_active': True,
            'attributes': {
                'surface': 'sand',
                'lights': True,
                'indoor': False,
                'capacity': 12
            },
            'images': []
        }
    ]
    
    print("Creating courts...")
    for data in courts_data:
        try:
            existing = Court.objects.filter(
                name_i18n__tk=data['name_i18n']['tk']
            ).first()
            
            if existing:
                print(f"⚠️  Court '{data['name_i18n']['tk']}' already exists")
            else:
                court = Court(**data)
                court.save()
                print(f"✅ Created: {data['name_i18n']['tk']} ({data['type']})")
        except Exception as e:
            print(f"❌ Error creating '{data['name_i18n']['tk']}': {e}")
    
    print(f"\n✅ Done! Total courts: {Court.objects.count()}")

if __name__ == '__main__':
    create_courts()

