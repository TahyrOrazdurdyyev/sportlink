"""
Notification models for MongoDB
"""
import uuid
from datetime import datetime
from mongoengine import Document, fields
from apps.users.models import User


class Notification(Document):
    """Notification model"""
    
    TYPE_CHOICES = [
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('opponent_matched', 'Opponent Matched'),
        ('match_reminder', 'Match Reminder'),
        ('payment_received', 'Payment Received'),
        ('tournament_update', 'Tournament Update'),
        ('system', 'System Notification'),
    ]
    
    # ID
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    
    # Recipient
    user = fields.ReferenceField(User, required=True, reverse_delete_rule=1)  # CASCADE
    
    # Notification details
    type = fields.StringField(choices=TYPE_CHOICES, required=True)
    title = fields.DictField(required=True)  # i18n: {'en': '...', 'ru': '...', 'tk': '...'}
    message = fields.DictField(required=True)  # i18n: {'en': '...', 'ru': '...', 'tk': '...'}
    
    # Additional data (for deep linking, etc.)
    data = fields.DictField()  # e.g., {'booking_id': '...', 'opponent_id': '...'}
    
    # Status
    is_read = fields.BooleanField(default=False)
    is_sent = fields.BooleanField(default=False)  # For push notifications
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    read_at = fields.DateTimeField()
    sent_at = fields.DateTimeField()
    
    meta = {
        'collection': 'notifications',
        'indexes': [
            'user',
            'type',
            'is_read',
            'created_at',
            [('user', 1), ('created_at', -1)],
            [('user', 1), ('is_read', 1)],
        ]
    }
    
    def __str__(self):
        return f"Notification {self.id} - {self.user}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            self.save()
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        if not self.is_sent:
            self.is_sent = True
            self.sent_at = datetime.utcnow()
            self.save()


class PushToken(Document):
    """Store user's push notification tokens"""
    
    PLATFORM_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
    ]
    
    # ID
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    
    # User and token
    user = fields.ReferenceField(User, required=True, reverse_delete_rule=1)
    token = fields.StringField(required=True, unique=True)
    platform = fields.StringField(choices=PLATFORM_CHOICES, required=True)
    
    # Status
    is_active = fields.BooleanField(default=True)
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    last_used_at = fields.DateTimeField()
    
    meta = {
        'collection': 'push_tokens',
        'indexes': [
            'user',
            'token',
            'is_active',
            [('user', 1), ('is_active', 1)],
        ]
    }
    
    def __str__(self):
        return f"PushToken {self.id} - {self.user} ({self.platform})"
    
    def save(self, *args, **kwargs):
        """Override save to update timestamps"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
