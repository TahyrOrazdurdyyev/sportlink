#!/usr/bin/env python
"""
Fix image URLs in database - replace localhost with correct IP
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.courts.models import Court
from apps.tournaments.models import Tournament

def fix_court_images():
    """Fix court image URLs"""
    courts = Court.objects.all()
    fixed_count = 0
    
    for court in courts:
        if court.images:
            updated = False
            new_images = []
            for img_url in court.images:
                if 'localhost' in img_url:
                    # Replace localhost with correct IP
                    new_url = img_url.replace('http://localhost:8000', 'http://192.168.31.106:8000')
                    new_images.append(new_url)
                    updated = True
                    print(f"Court {court.id}: {img_url} -> {new_url}")
                else:
                    new_images.append(img_url)
            
            if updated:
                court.images = new_images
                court.save()
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} courts")

def fix_tournament_images():
    """Fix tournament image URLs"""
    tournaments = Tournament.objects.all()
    fixed_count = 0
    
    for tournament in tournaments:
        if tournament.image_url and 'localhost' in tournament.image_url:
            old_url = tournament.image_url
            tournament.image_url = old_url.replace('http://localhost:8000', 'http://192.168.31.106:8000')
            tournament.save()
            fixed_count += 1
            print(f"Tournament {tournament.id}: {old_url} -> {tournament.image_url}")
    
    print(f"\nFixed {fixed_count} tournaments")

if __name__ == '__main__':
    print("Fixing court image URLs...")
    fix_court_images()
    
    print("\nFixing tournament image URLs...")
    fix_tournament_images()
    
    print("\nDone!")

