"""
Subscription Plan models for MongoDB
"""
import uuid
from datetime import datetime
from mongoengine import Document, fields


class SubscriptionPlan(Document):
    """Subscription Plan for users (Sport+, ProSport, ClubPremium)"""
    
    # ID
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    
    # Plan details
    name = fields.DictField(required=True)  # {'tk': 'Sport+', 'ru': 'Спорт+', 'en': 'Sport+'}
    description = fields.DictField()  # {'tk': '...', 'ru': '...', 'en': '...'}
    
    # Pricing
    monthly_price = fields.FloatField(required=True)  # Price per month
    yearly_price = fields.FloatField(required=True)  # Price per year
    currency = fields.StringField(default='TMT', max_length=3)
    
    # Discount
    discount_percentage = fields.FloatField(default=0.0, min_value=0.0, max_value=100.0)  # Discount in percentage (0-100)
    
    # Features (enabled/disabled)
    features = fields.DictField(required=True)  # {'court_booking': True, 'opponent_matching': False, ...}
    
    # Booking Restrictions
    booking_limits = fields.DictField(default=dict)  # Booking restrictions configuration
    # Structure:
    # {
    #   'bookings_per_week': 2,  # Number of bookings allowed per week
    #   'max_duration_hours': 2,  # Maximum duration per booking in hours
    #   'allowed_days': [1, 2, 3, 4, 5],  # Days of week (1=Monday, 7=Sunday)
    # }
    
    # Display order
    order = fields.IntField(default=0)
    
    # Status
    is_active = fields.BooleanField(default=True)
    is_popular = fields.BooleanField(default=False)  # "Most Popular" badge
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'subscription_plans',
        'indexes': [
            'is_active',
            'order',
            'created_at',
        ],
        'ordering': ['order'],
    }
    
    def __str__(self):
        return self.name.get('en', 'Unknown Plan')
    
    def get_discounted_monthly_price(self):
        """Calculate monthly price with discount applied"""
        if self.discount_percentage > 0:
            return self.monthly_price * (1 - self.discount_percentage / 100)
        return self.monthly_price
    
    def get_discounted_yearly_price(self):
        """Calculate yearly price with discount applied"""
        if self.discount_percentage > 0:
            return self.yearly_price * (1 - self.discount_percentage / 100)
        return self.yearly_price
    
    def has_discount(self):
        """Check if plan has an active discount"""
        return self.discount_percentage > 0
    
    def get_bookings_per_week(self):
        """Get number of bookings allowed per week"""
        return self.booking_limits.get('bookings_per_week', 0)
    
    def get_max_duration_hours(self):
        """Get maximum duration per booking in hours"""
        return self.booking_limits.get('max_duration_hours', 0)
    
    def get_allowed_days(self):
        """Get list of allowed days (1=Monday, 7=Sunday)"""
        return self.booking_limits.get('allowed_days', [])
    
    def is_day_allowed(self, day_of_week):
        """Check if a specific day is allowed for booking (1=Monday, 7=Sunday)"""
        allowed_days = self.get_allowed_days()
        return day_of_week in allowed_days if allowed_days else True
    
    def save(self, *args, **kwargs):
        """Override save to update timestamps"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


# Available features that can be enabled/disabled
AVAILABLE_FEATURES = {
    'court_booking': {
        'name': {'tk': 'Meýdança ärendasy', 'ru': 'Аренда площадки', 'en': 'Court Booking'},
        'description': {'tk': 'Sport meýdançalaryny ärendä almak mümkinçiligi', 'ru': 'Возможность аренды спортивных площадок', 'en': 'Ability to book sport courts'},
    },
    'opponent_matching': {
        'name': {'tk': 'Garşydaş gözleg', 'ru': 'Подбор соперника', 'en': 'Opponent Matching'},
        'description': {'tk': 'Deň derejeli garşydaş tapmak', 'ru': 'Подбор соперника соответствующего уровня', 'en': 'Find opponents of matching skill level'},
    },
    'weekend_booking': {
        'name': {'tk': 'Dynç günleri bronlaş', 'ru': 'Бронирование в выходные', 'en': 'Weekend Booking'},
        'description': {'tk': 'Şenbe we ýekşenbe günleri bronlamak', 'ru': 'Возможность бронирования в субботу и воскресенье', 'en': 'Book courts on Saturday and Sunday'},
    },
    'tournament_registration': {
        'name': {'tk': 'Ýaryşlara gatnaşmak', 'ru': 'Регистрация на турниры', 'en': 'Tournament Registration'},
        'description': {'tk': 'Ýaryşlara hasaba alynmak mümkinçiligi', 'ru': 'Возможность регистрации на турниры', 'en': 'Ability to register for tournaments'},
    },
    'equipment_rental': {
        'name': {'tk': 'Enjam ärendasy', 'ru': 'Аренда экипировки', 'en': 'Equipment Rental'},
        'description': {'tk': 'Sport enjamlaryny ärendä almak (raketka, top we ş.m.)', 'ru': 'Аренда спортивной экипировки (ракетки, мячи и т.д.)', 'en': 'Rent sports equipment (rackets, balls, etc.)'},
    },
    'advanced_statistics': {
        'name': {'tk': 'Giňişleýin statistika', 'ru': 'Расширенная статистика', 'en': 'Advanced Statistics'},
        'description': {'tk': 'Jikme-jik oýun statistikasy', 'ru': 'Подробная статистика игр', 'en': 'Detailed game statistics'},
    },
    'discount_court_booking': {
        'name': {'tk': 'Arzanladyş (ärendä)', 'ru': 'Скидка на аренду', 'en': 'Court Booking Discount'},
        'description': {'tk': 'Meýdança ärendasy üçin arzanladyş', 'ru': 'Скидка на аренду площадок', 'en': 'Discount on court bookings'},
    },
}

