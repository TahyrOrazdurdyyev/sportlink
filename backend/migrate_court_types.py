#!/usr/bin/env python
"""
Migrate court types from old values to category IDs
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.courts.models import Court
from apps.categories.models import Category

def migrate_court_types():
    """Update court types to use category IDs"""
    
    # Mapping old types to category names
    type_mapping = {
        'tennis': 'Tennis',
        'football': 'Football', 
        'basketball': 'Basketball',
        'volleyball': 'Volleyball',
        'gym': 'Gym',
        'other': 'Other',
    }
    
    courts = Court.objects.all()
    categories = {cat.name_i18n.get('en', ''): str(cat.id) for cat in Category.objects.all()}
    
    print(f"Found {courts.count()} courts")
    print(f"Found {len(categories)} categories")
    print(f"Categories: {categories}\n")
    
    updated = 0
    for court in courts:
        old_type = court.type
        
        # Skip if already using category ID (24 character hex string)
        if len(old_type) == 24:
            print(f"⚠️  {court.get_name('tk')} - already using category ID")
            continue
        
        # Try to find matching category
        if old_type in type_mapping:
            category_name = type_mapping[old_type]
            if category_name in categories:
                new_type = categories[category_name]
                court.type = new_type
                court.save()
                updated += 1
                print(f"✅ {court.get_name('tk')}: {old_type} → {category_name} ({new_type})")
            else:
                print(f"❌ {court.get_name('tk')}: Category '{category_name}' not found")
        else:
            print(f"⚠️  {court.get_name('tk')}: Unknown type '{old_type}'")
    
    print(f"\n✅ Updated {updated} courts")

if __name__ == '__main__':
    migrate_court_types()

