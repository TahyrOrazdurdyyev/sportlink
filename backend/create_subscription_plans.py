"""
Create initial subscription plans
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportlink.settings')
django.setup()

from apps.subscriptions.models import SubscriptionPlan

def create_plans():
    """Create Sport+, ProSport, and ClubPremium plans"""
    
    # Clear existing plans
    SubscriptionPlan.objects.all().delete()
    print("Cleared existing plans")
    
    # Sport+ (Basic)
    sport_plus = SubscriptionPlan(
        name={'tk': 'Sport+', 'ru': 'Спорт+', 'en': 'Sport+'},
        description={
            'tk': 'Esasy funksiýalar bilen',
            'ru': 'Базовый план с основными функциями',
            'en': 'Basic plan with essential features'
        },
        monthly_price=50.0,
        yearly_price=500.0,
        currency='TMT',
        features={
            'court_booking': True,
            'opponent_matching': False,
            'weekend_booking': False,
            'tournament_registration': False,
            'equipment_rental': False,
            'advanced_statistics': False,
            'discount_court_booking': False,
        },
        order=1,
        is_active=True,
        is_popular=False,
    )
    sport_plus.save()
    print(f"Created: {sport_plus.name['en']}")
    
    # ProSport (Professional)
    pro_sport = SubscriptionPlan(
        name={'tk': 'ProSport', 'ru': 'ПроСпорт', 'en': 'ProSport'},
        description={
            'tk': 'Hünärmenler üçin ähli mümkinçilikler',
            'ru': 'Все возможности для профессионалов',
            'en': 'All features for professionals'
        },
        monthly_price=100.0,
        yearly_price=1000.0,
        currency='TMT',
        features={
            'court_booking': True,
            'opponent_matching': True,
            'weekend_booking': True,
            'tournament_registration': False,
            'equipment_rental': True,
            'advanced_statistics': True,
            'discount_court_booking': False,
        },
        order=2,
        is_active=True,
        is_popular=True,  # Most popular
    )
    pro_sport.save()
    print(f"Created: {pro_sport.name['en']} (Popular)")
    
    # ClubPremium (Premium)
    club_premium = SubscriptionPlan(
        name={'tk': 'ClubPremium', 'ru': 'КлубПремиум', 'en': 'ClubPremium'},
        description={
            'tk': 'Iň gowy mümkinçilikler we arzanladyşlar',
            'ru': 'Максимум возможностей и скидок',
            'en': 'Maximum features and discounts'
        },
        monthly_price=150.0,
        yearly_price=1500.0,
        currency='TMT',
        features={
            'court_booking': True,
            'opponent_matching': True,
            'weekend_booking': True,
            'tournament_registration': True,
            'equipment_rental': True,
            'advanced_statistics': True,
            'discount_court_booking': True,
        },
        order=3,
        is_active=True,
        is_popular=False,
    )
    club_premium.save()
    print(f"Created: {club_premium.name['en']}")
    
    print("\n✅ Successfully created 3 subscription plans!")
    print(f"Total plans: {SubscriptionPlan.objects.count()}")


if __name__ == '__main__':
    create_plans()

