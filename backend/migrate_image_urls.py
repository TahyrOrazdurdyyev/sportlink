"""
Migration script to update image URLs in database from old IP to new IP
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.courts.models import Court
from apps.tournaments.models import Tournament
from apps.users.models import User

OLD_IP = 'http://192.168.1.97:8000'
NEW_IP = 'http://192.168.1.64:8000'

def update_court_images():
    """Update court image URLs"""
    updated_count = 0
    for court in Court.objects.all():
        if court.images:
            new_images = []
            changed = False
            for img_url in court.images:
                if img_url and img_url.startswith(OLD_IP):
                    # Replace old IP with new IP
                    new_url = img_url.replace(OLD_IP, NEW_IP)
                    new_images.append(new_url)
                    changed = True
                    print(f"Updated: {img_url} -> {new_url}")
                else:
                    new_images.append(img_url)
            
            if changed:
                court.images = new_images
                court.save()
                updated_count += 1
    
    print(f"\nUpdated {updated_count} courts")
    return updated_count

def update_tournament_images():
    """Update tournament image URLs"""
    updated_count = 0
    for tournament in Tournament.objects.all():
        if tournament.image_url and tournament.image_url.startswith(OLD_IP):
            old_url = tournament.image_url
            tournament.image_url = tournament.image_url.replace(OLD_IP, NEW_IP)
            tournament.save()
            updated_count += 1
            print(f"Updated tournament: {old_url} -> {tournament.image_url}")
    
    print(f"\nUpdated {updated_count} tournaments")
    return updated_count

def update_user_avatars():
    """Update user avatar URLs"""
    updated_count = 0
    for user in User.objects.all():
        if user.avatar_url and user.avatar_url.startswith(OLD_IP):
            old_url = user.avatar_url
            user.avatar_url = user.avatar_url.replace(OLD_IP, NEW_IP)
            user.save()
            updated_count += 1
            print(f"Updated user avatar: {old_url} -> {user.avatar_url}")
    
    print(f"\nUpdated {updated_count} users")
    return updated_count

if __name__ == '__main__':
    print(f"Starting migration: Updating URLs from {OLD_IP} to {NEW_IP}\n")
    print("=" * 80)
    
    print("\n1. Updating court images...")
    courts_updated = update_court_images()
    
    print("\n2. Updating tournament images...")
    tournaments_updated = update_tournament_images()
    
    print("\n3. Updating user avatars...")
    users_updated = update_user_avatars()
    
    print("\n" + "=" * 80)
    print(f"\nMigration completed!")
    print(f"Total updated: {courts_updated} courts, {tournaments_updated} tournaments, {users_updated} users")
    print("\nIMPORTANT: For production deployment, update OLD_IP and NEW_IP variables in this script")

