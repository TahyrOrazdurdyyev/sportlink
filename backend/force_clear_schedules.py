"""
Force clear all availability_schedule data
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from pymongo import MongoClient
from django.conf import settings

def clear_all_availability_schedules():
    """Clear all availability_schedule fields"""
    
    # Connect directly to MongoDB
    client = MongoClient(
        host=settings.MONGODB_HOST,
        port=settings.MONGODB_PORT,
        username=settings.MONGODB_USERNAME or None,
        password=settings.MONGODB_PASSWORD or None,
    )
    db = client[settings.MONGODB_NAME]
    users_collection = db['users']  # Correct collection name
    
    print("Clearing ALL availability_schedule fields from all users...\n")
    
    # Update all users - set availability_schedule to empty array
    result = users_collection.update_many(
        {},  # All users
        {'$set': {'availability_schedule': []}}
    )
    
    print(f"Updated {result.modified_count} users")
    print("All availability schedules have been cleared.")
    print("Users will need to set their schedules again in the app.")
    
    client.close()

if __name__ == '__main__':
    print("=" * 80)
    clear_all_availability_schedules()
    print("=" * 80)

