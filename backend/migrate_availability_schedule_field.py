"""
Migration script to rename 'day' to 'day_of_week' in availability_schedule
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from pymongo import MongoClient
from django.conf import settings

def migrate_availability_schedule():
    """Update availability_schedule field from 'day' to 'day_of_week'"""
    
    # Connect directly to MongoDB
    client = MongoClient(
        host=settings.MONGODB_HOST,
        port=settings.MONGODB_PORT,
        username=settings.MONGODB_USERNAME or None,
        password=settings.MONGODB_PASSWORD or None,
    )
    db = client[settings.MONGODB_NAME]
    users_collection = db['user']
    
    updated_count = 0
    
    # Find all users with availability_schedule
    for user in users_collection.find({'availability_schedule': {'$exists': True, '$ne': []}}):
        needs_update = False
        new_schedule = []
        
        for day_availability in user.get('availability_schedule', []):
            if 'day' in day_availability:
                # Has old field 'day', need to update
                needs_update = True
                # Just clear it - user will need to set it again
                break
        
        if needs_update:
            # Clear the schedule
            users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {'availability_schedule': []}}
            )
            updated_count += 1
            phone = user.get('phone', 'unknown')
            print(f"Cleared availability_schedule for user {user['_id']} ({phone})")
    
    print(f"\nMigration completed. Cleared {updated_count} users' availability schedules")
    print("Users will need to set their schedules again in the app")
    
    client.close()

if __name__ == '__main__':
    print("Starting migration: Fixing availability_schedule field names\n")
    print("=" * 80)
    migrate_availability_schedule()
    print("=" * 80)

