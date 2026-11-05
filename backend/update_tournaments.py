#!/usr/bin/env python
"""
Update existing tournaments with new fields
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.tournaments.models import Tournament

def update_tournaments():
    """Add new fields to existing tournaments"""
    
    tournaments = Tournament.objects.all()
    
    print(f"Found {tournaments.count()} tournaments. Updating...\n")
    
    for tournament in tournaments:
        updated = False
        
        if not tournament.country:
            tournament.country = "Turkmenistan"
            updated = True
        
        if not tournament.city:
            tournament.city = "Ashgabat"
            updated = True
        
        if not tournament.organizer_name:
            tournament.organizer_name = "Sportlink Platform"
            updated = True
        
        if updated:
            tournament.save()
            print(f"✅ Updated: {tournament.get_name('tk')}")
            print(f"   Country: {tournament.country}, City: {tournament.city}")
            print(f"   Organizer: {tournament.organizer_name}")
        else:
            print(f"⚠️  {tournament.get_name('tk')} - already up to date")
    
    print(f"\n✅ Done!")

if __name__ == '__main__':
    update_tournaments()

