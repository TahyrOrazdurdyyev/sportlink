"""
Check availability_schedule in database
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from pymongo import MongoClient
from django.conf import settings

def check_availability_schedule():
    """Check availability_schedule in all users"""
    
    # Connect directly to MongoDB
    client = MongoClient(
        host=settings.MONGODB_HOST,
        port=settings.MONGODB_PORT,
        username=settings.MONGODB_USERNAME or None,
        password=settings.MONGODB_PASSWORD or None,
    )
    db = client[settings.MONGODB_NAME]
    users_collection = db['user']
    
    print("Checking all users for availability_schedule...\n")
    
    for user in users_collection.find():
        user_id = user.get('_id')
        phone = user.get('phone', 'unknown')
        schedule = user.get('availability_schedule', [])
        
        if schedule:
            print(f"\nUser: {user_id} ({phone})")
            print(f"  Has {len(schedule)} schedule entries")
            for idx, day_avail in enumerate(schedule):
                print(f"  Entry {idx}: {day_avail}")
                if 'day' in day_avail:
                    print(f"    ⚠️  HAS OLD FIELD 'day'!")
                if 'day_of_week' in day_avail:
                    print(f"    ✓ Has new field 'day_of_week'")
    
    client.close()

if __name__ == '__main__':
    check_availability_schedule()

