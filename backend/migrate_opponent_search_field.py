"""
Migration script to add available_for_opponent_search field to existing users
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.users.models import User


def migrate_opponent_search_field():
    """Add available_for_opponent_search field to all users"""
    print("Starting migration: Adding available_for_opponent_search field...")
    
    users = User.objects.all()
    total = users.count()
    updated = 0
    
    print(f"Found {total} users")
    
    for user in users:
        # Check if field exists and set default if not
        if not hasattr(user, 'available_for_opponent_search') or user.available_for_opponent_search is None:
            user.available_for_opponent_search = True
            user.save()
            updated += 1
            
            if updated % 100 == 0:
                print(f"Updated {updated}/{total} users...")
    
    print(f"\nMigration completed!")
    print(f"Total users: {total}")
    print(f"Updated users: {updated}")
    print(f"All users now have available_for_opponent_search field set to True by default")


if __name__ == '__main__':
    try:
        migrate_opponent_search_field()
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

