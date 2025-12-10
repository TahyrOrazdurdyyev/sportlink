"""
Court models for MongoDB
"""
import uuid
from datetime import datetime
from mongoengine import Document, EmbeddedDocument, fields
from apps.users.models import User


class Tariff(EmbeddedDocument):
    """Embedded tariff for courts"""
    name_i18n = fields.DictField(default=dict)
    description_i18n = fields.DictField(default=dict)
    base_price = fields.DecimalField(min_value=0, precision=2)
    price_type = fields.StringField(choices=['per_hour', 'per_day', 'per_slot'], default='per_hour')
    items_included = fields.DictField(default=dict)  # {"racket": true, "balls": 2, ...}
    min_booking_hours = fields.IntField(min_value=1, default=1)
    max_booking_hours = fields.IntField(min_value=1, default=24)
    active_from = fields.DateTimeField()
    active_to = fields.DateTimeField()


class AvailabilitySlot(EmbeddedDocument):
    """Embedded availability slot"""
    start_time = fields.DateTimeField(required=True)
    end_time = fields.DateTimeField(required=True)
    status = fields.StringField(
        choices=['free', 'booked', 'blocked'], 
        default='free'
    )
    booking_id = fields.UUIDField()  # Reference to booking


class Court(Document):
    """Sports court/field for MongoDB"""
    
    COURT_TYPE_CHOICES = [
        ('tennis', 'Tennis'),
        ('football', 'Football'),
        ('basketball', 'Basketball'),
        ('volleyball', 'Volleyball'),
        ('gym', 'Gym'),
        ('other', 'Other'),
    ]
    
    # ID
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    
    # Basic info
    name_i18n = fields.DictField(default=dict)  # Multilingual name
    address = fields.StringField(required=True)
    location = fields.PointField(required=True)  # MongoDB GeoJSON point
    type = fields.StringField(choices=COURT_TYPE_CHOICES, required=True)
    
    # Ownership
    owner = fields.ReferenceField(User, reverse_delete_rule=2)  # NULLIFY
    created_by = fields.ReferenceField(User, reverse_delete_rule=2)  # NULLIFY
    
    # Attributes and media
    attributes = fields.DictField(default=dict)  # {surface_type, lights, indoor, etc.}
    images = fields.ListField(fields.URLField())  # List of image URLs
    
    # Tariffs
    tariffs = fields.ListField(fields.EmbeddedDocumentField(Tariff))
    
    # Availability (embedded slots)
    availability_slots = fields.ListField(fields.EmbeddedDocumentField(AvailabilitySlot))
    
    # Status
    is_active = fields.BooleanField(default=True)
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'courts',
        'indexes': [
            'location',  # 2dsphere index for geo queries
            'type',
            'owner',
            'created_by',
            'is_active',
            'created_at',
            [('availability_slots.start_time', 1), ('availability_slots.end_time', 1)],  # Compound index for time queries
        ]
    }
    
    def __str__(self):
        return self.name_i18n.get('tk', self.name_i18n.get('ru', self.name_i18n.get('en', str(self.id))))
    
    def save(self, *args, **kwargs):
        """Override save to update timestamps"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def get_name(self, language='tk'):
        """Get name in specified language"""
        return self.name_i18n.get(language, self.name_i18n.get('tk', ''))
    
    def get_availability_for_date(self, date):
        """Get availability slots for a specific date"""
        # Filter slots by date
        from datetime import time
        start_of_day = datetime.combine(date, time.min)
        end_of_day = datetime.combine(date, time.max)
        
        return [
            slot for slot in self.availability_slots
            if start_of_day <= slot.start_time <= end_of_day
        ]
    
    def is_available(self, start_time, end_time):
        """Check if court is available for the given time range"""
        for slot in self.availability_slots:
            # Check for overlapping slots that are not free
            if (slot.status != 'free' and 
                slot.start_time < end_time and 
                slot.end_time > start_time):
                return False
        return True
