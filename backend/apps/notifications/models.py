"""
Notification models for MongoDB
"""
import uuid
from datetime import datetime
from mongoengine import Document, fields
from apps.users.models import User


class Notification(Document):
    """Notification model for MongoDB"""
    
    TYPE_CHOICES = [
        ('push', 'Push Notification'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in_app', 'In-App Notification'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    EVENT_TYPE_CHOICES = [
        ('tournament_created', 'Tournament Created'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('tournament_registration_open', 'Tournament Registration Open'),
        ('tournament_reminder', 'Tournament Reminder'),
        ('match_invite', 'Match Invitation'),
        ('partner_request', 'Partner Request'),
        ('payment_reminder', 'Payment Reminder'),
        ('system_announcement', 'System Announcement'),
    ]
    
    # ID
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    
    # Target user
    user = fields.ReferenceField(User, required=True, reverse_delete_rule=1)  # CASCADE
    
    # Notification details
    type = fields.StringField(choices=TYPE_CHOICES, required=True)
    event_type = fields.StringField(choices=EVENT_TYPE_CHOICES)
    priority = fields.StringField(choices=PRIORITY_CHOICES, default='normal')
    
    # Content
    title = fields.StringField(max_length=200, required=True)
    message = fields.StringField(max_length=1000, required=True)
    
    # Multilingual content (optional)
    title_i18n = fields.DictField()  # {"tk": "...", "ru": "...", "en": "..."}
    message_i18n = fields.DictField()  # {"tk": "...", "ru": "...", "en": "..."}
    
    # Payload data (additional info for the app)
    payload = fields.DictField(default=dict)
    # Example payload structures:
    # Tournament: {"tournament_id": "uuid", "start_date": "...", "location": "..."}
    # Booking: {"booking_id": "uuid", "court_name": "...", "start_time": "..."}
    # Match: {"match_id": "uuid", "opponent": "...", "court": "..."}
    
    # Delivery tracking
    sent_at = fields.DateTimeField()
    delivered_at = fields.DateTimeField()
    read_at = fields.DateTimeField()
    clicked_at = fields.DateTimeField()
    
    # Status
    is_sent = fields.BooleanField(default=False)
    is_delivered = fields.BooleanField(default=False)
    is_read = fields.BooleanField(default=False)
    is_clicked = fields.BooleanField(default=False)
    
    # Failure tracking
    failed = fields.BooleanField(default=False)
    failure_reason = fields.StringField(max_length=500)
    retry_count = fields.IntField(default=0)
    max_retries = fields.IntField(default=3)
    
    # Scheduling
    scheduled_at = fields.DateTimeField()  # For delayed notifications
    expires_at = fields.DateTimeField()    # Notification expiration
    
    # Action button (optional)
    action_url = fields.URLField()  # Deep link or web URL
    action_text = fields.StringField(max_length=50)  # Button text
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'notifications',
        'indexes': [
            'user',
            'type',
            'event_type',
            'priority',
            'is_sent',
            'is_delivered',
            'is_read',
            'failed',
            'scheduled_at',
            'expires_at',
            'created_at',
            [('user', 1), ('created_at', -1)],  # User's notifications by date
            [('user', 1), ('is_read', 1)],      # User's unread notifications
            [('scheduled_at', 1), ('is_sent', 1)],  # Pending scheduled notifications
        ]
    }
    
    def __str__(self):
        return f"Notification {self.id} - {self.user} - {self.title}"
    
    def save(self, *args, **kwargs):
        """Override save to update timestamps"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    def get_title(self, language='tk'):
        """Get title in specified language"""
        if self.title_i18n and language in self.title_i18n:
            return self.title_i18n[language]
        return self.title
    
    def get_message(self, language='tk'):
        """Get message in specified language"""
        if self.message_i18n and language in self.message_i18n:
            return self.message_i18n[language]
        return self.message
    
    def mark_sent(self):
        """Mark notification as sent"""
        self.is_sent = True
        self.sent_at = datetime.utcnow()
        self.save()
    
    def mark_delivered(self):
        """Mark notification as delivered"""
        self.is_delivered = True
        self.delivered_at = datetime.utcnow()
        self.save()
    
    def mark_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
        self.save()
    
    def mark_clicked(self):
        """Mark notification as clicked"""
        self.is_clicked = True
        self.clicked_at = datetime.utcnow()
        if not self.is_read:
            self.mark_read()
        self.save()
    
    def mark_failed(self, reason=""):
        """Mark notification as failed"""
        self.failed = True
        self.failure_reason = reason
        self.retry_count += 1
        self.save()
    
    def can_retry(self):
        """Check if notification can be retried"""
        return self.failed and self.retry_count < self.max_retries
    
    def reset_for_retry(self):
        """Reset notification for retry"""
        if self.can_retry():
            self.failed = False
            self.failure_reason = ""
            self.is_sent = False
            self.sent_at = None
            self.save()
    
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
