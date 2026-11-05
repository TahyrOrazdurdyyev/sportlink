"""
Script to initialize equipment for sport categories
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.categories.models import Category

# Equipment data for different sports
EQUIPMENT_DATA = {
    'Football': [
        {'key': 'balls', 'name_i18n': {'en': 'Balls', 'ru': 'Мячи', 'tk': 'Toplar'}},
        {'key': 'shin_guards', 'name_i18n': {'en': 'Shin Guards', 'ru': 'Щитки', 'tk': 'Baldyr goragçylary'}},
        {'key': 'jerseys', 'name_i18n': {'en': 'Jerseys', 'ru': 'Майки', 'tk': 'Maýkalar'}},
    ],
    'Tennis': [
        {'key': 'rackets', 'name_i18n': {'en': 'Rackets', 'ru': 'Ракетки', 'tk': 'Raketler'}},
        {'key': 'balls', 'name_i18n': {'en': 'Tennis Balls', 'ru': 'Теннисные мячи', 'tk': 'Tennis toplary'}},
    ],
    'Basketball': [
        {'key': 'balls', 'name_i18n': {'en': 'Basketballs', 'ru': 'Баскетбольные мячи', 'tk': 'Basketbol toplary'}},
        {'key': 'jerseys', 'name_i18n': {'en': 'Jerseys', 'ru': 'Майки', 'tk': 'Maýkalar'}},
    ],
    'Volleyball': [
        {'key': 'balls', 'name_i18n': {'en': 'Volleyballs', 'ru': 'Волейбольные мячи', 'tk': 'Woleýbol toplary'}},
        {'key': 'knee_pads', 'name_i18n': {'en': 'Knee Pads', 'ru': 'Наколенники', 'tk': 'Dyz goragçylary'}},
    ],
    'Badminton': [
        {'key': 'rackets', 'name_i18n': {'en': 'Rackets', 'ru': 'Ракетки', 'tk': 'Raketler'}},
        {'key': 'shuttlecocks', 'name_i18n': {'en': 'Shuttlecocks', 'ru': 'Воланы', 'tk': 'Wolanlar'}},
    ],
    'Table Tennis': [
        {'key': 'paddles', 'name_i18n': {'en': 'Paddles', 'ru': 'Ракетки', 'tk': 'Raketler'}},
        {'key': 'balls', 'name_i18n': {'en': 'Ping Pong Balls', 'ru': 'Мячи для настольного тенниса', 'tk': 'Stol tennisi toplary'}},
    ],
}

def init_equipment():
    """Initialize equipment for all categories"""
    updated_count = 0
    
    for category in Category.objects.all():
        # Try to match category name with equipment data
        category_name_en = category.name_i18n.get('en', '').strip()
        
        if category_name_en in EQUIPMENT_DATA:
            equipment = EQUIPMENT_DATA[category_name_en]
            category.available_equipment = equipment
            category.save()
            print(f"✅ Updated equipment for '{category_name_en}': {len(equipment)} items")
            updated_count += 1
        else:
            # Check if category name contains any of the sport names
            for sport_name, equipment in EQUIPMENT_DATA.items():
                if sport_name.lower() in category_name_en.lower():
                    category.available_equipment = equipment
                    category.save()
                    print(f"✅ Updated equipment for '{category_name_en}' (matched '{sport_name}'): {len(equipment)} items")
                    updated_count += 1
                    break
    
    print(f"\n✅ Total categories updated: {updated_count}")
    print(f"📋 Total categories: {Category.objects.count()}")

if __name__ == '__main__':
    print("🔧 Initializing equipment for sport categories...\n")
    init_equipment()
    print("\n✅ Done!")

