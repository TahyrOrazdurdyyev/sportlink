"""
Booking models for MongoDB
"""
import uuid
from datetime import datetime
from mongoengine import Document, fields
from apps.users.models import User
from apps.courts.models import Court


class Booking(Document):
    """Booking/Reservation model for MongoDB"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),  # For future use
        ('online', 'Online'),  # For future use
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]
    
    # ID
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    
    # Booking details
    user = fields.ReferenceField(User, required=True, reverse_delete_rule=1)  # CASCADE
    court = fields.ReferenceField(Court, required=True, reverse_delete_rule=1)  # CASCADE
    
    # Time
    start_time = fields.DateTimeField(required=True)
    end_time = fields.DateTimeField(required=True)
    
    # Status
    status = fields.StringField(choices=STATUS_CHOICES, default='pending')
    
    # Participants (other users involved)
    participants = fields.ListField(fields.ReferenceField(User))
    
    # Pricing
    tariff_snapshot = fields.DictField()  # Snapshot of tariff at booking time
    total_price = fields.DecimalField(min_value=0, precision=2)
    
    # Payment
    payment_method = fields.StringField(choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_status = fields.StringField(choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Additional info
    notes = fields.StringField(max_length=500)
    cancellation_reason = fields.StringField(max_length=500)
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    cancelled_at = fields.DateTimeField()
    
    meta = {
        'collection': 'bookings',
        'indexes': [
            'user',
            'court',
            'status',
            'start_time',
            'end_time',
            'created_at',
            'payment_status',
            [('court', 1), ('start_time', 1), ('end_time', 1)],  # Compound index for availability checks
            [('user', 1), ('start_time', -1)],  # User's bookings sorted by time
        ]
    }
    
    def __str__(self):
        return f"Booking {self.id} - {self.user} at {self.court}"
    
    def save(self, *args, **kwargs):
        """Override save to update timestamps and validate"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Validate time range
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError("End time must be after start time")
        
        return super().save(*args, **kwargs)
    
    def clean(self):
        """Validation before saving"""
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValueError("End time must be after start time")
            
            # Check for overlapping bookings (only for new bookings)
            if not self.pk:  # New booking
                overlapping = Booking.objects(
                    court=self.court,
                    status__in=['confirmed', 'pending'],
                    start_time__lt=self.end_time,
                    end_time__gt=self.start_time
                ).count()
                
                if overlapping > 0:
                    raise ValueError("This time slot is already booked")
    
    def duration_hours(self):
        """Get booking duration in hours"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 3600
        return 0
    
    def can_cancel(self):
        """Check if booking can be cancelled"""
        if self.status in ['cancelled', 'completed']:
            return False
        
        # Can cancel if more than 2 hours before start time
        if self.start_time:
            from datetime import timedelta
            return datetime.utcnow() < (self.start_time - timedelta(hours=2))
        
        return True
    
    def cancel(self, reason=""):
        """Cancel the booking"""
        if not self.can_cancel():
            raise ValueError("Booking cannot be cancelled")
        
        self.status = 'cancelled'
        self.cancellation_reason = reason
        self.cancelled_at = datetime.utcnow()
        self.save()
    
    def confirm(self):
        """Confirm the booking"""
        if self.status == 'pending':
            self.status = 'confirmed'
            self.save()
    
    def complete(self):
        """Mark booking as completed"""
        if self.status == 'confirmed':
            self.status = 'completed'
            self.save()
