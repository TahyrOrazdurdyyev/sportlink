"""
Subscription Plan models for MongoDB
"""
import uuid
from datetime import datetime
from mongoengine import Document, EmbeddedDocument, fields


class SubscriptionFeature(EmbeddedDocument):
    """Feature that can be enabled/disabled for subscription plan"""
    feature_key = fields.StringField(required=True, max_length=50)  # e.g., 'court_booking', 'opponent_matching'
    enabled = fields.BooleanField(default=True)
    
    meta = {
        'strict': False,
    }


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
    
    # Features
    features = fields.DictField(required=True)  # {'court_booking': True, 'opponent_matching': False, ...}
    
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
    'priority_support': {
        'name': {'tk': 'Ileri tutma goldawy', 'ru': 'Приоритетная поддержка', 'en': 'Priority Support'},
        'description': {'tk': 'Çalt goldaw hyzmaty', 'ru': 'Быстрая поддержка клиентов', 'en': 'Fast customer support'},
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

