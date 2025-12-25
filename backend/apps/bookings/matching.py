"""
Opponent matching logic for bookings
"""
import uuid
from datetime import datetime, timedelta
from mongoengine import Document, fields
from apps.users.models import User
from apps.bookings.models import Booking


class OpponentMatch(Document):
    """Model to track opponent matches"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),  # Waiting for opponent acceptance
        ('accepted', 'Accepted'),  # Opponent accepted
        ('declined', 'Declined'),  # Opponent declined
        ('matched', 'Matched'),  # Successfully matched
        ('cancelled', 'Cancelled'),  # Match cancelled
    ]
    
    # ID
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    
    # Match details
    booking = fields.ReferenceField(Booking, required=True, reverse_delete_rule=1)  # CASCADE
    seeker = fields.ReferenceField(User, required=True)  # User looking for opponent
    opponent = fields.ReferenceField(User)  # Matched opponent
    
    # Match info
    status = fields.StringField(choices=STATUS_CHOICES, default='pending')
    opponents_needed = fields.IntField(min_value=1, default=1)
    opponents_found = fields.IntField(min_value=0, default=0)
    
    # Notifications
    seeker_notified = fields.BooleanField(default=False)
    opponent_notified = fields.BooleanField(default=False)
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    matched_at = fields.DateTimeField()
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'opponent_matches',
        'indexes': [
            'booking',
            'seeker',
            'opponent',
            'status',
            'created_at',
            [('booking', 1), ('status', 1)],
        ]
    }
    
    def __str__(self):
        return f"Match {self.id} - {self.seeker} vs {self.opponent}"
    
    def save(self, *args, **kwargs):
        """Override save to update timestamps"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


class OpponentRequest(Document):
    """Model for users looking for opponents"""
    
    # ID
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    
    # Request details
    user = fields.ReferenceField(User, required=True)
    booking = fields.ReferenceField(Booking, required=True, reverse_delete_rule=1)
    
    # Preferences
    skill_level = fields.StringField(choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('any', 'Any'),
    ], default='any')
    
    # Status
    is_active = fields.BooleanField(default=True)
    is_matched = fields.BooleanField(default=False)
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    expires_at = fields.DateTimeField()
    
    meta = {
        'collection': 'opponent_requests',
        'indexes': [
            'user',
            'booking',
            'is_active',
            'is_matched',
            'created_at',
            'expires_at',
        ]
    }
    
    def __str__(self):
        return f"Request {self.id} - {self.user}"
    
    def save(self, *args, **kwargs):
        """Override save to set expiration"""
        if not self.expires_at and self.booking:
            # Request expires 1 hour before booking start time
            self.expires_at = self.booking.start_time - timedelta(hours=1)
        return super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if request is expired"""
        return datetime.utcnow() >= self.expires_at


def find_opponent_for_booking(booking):
    """
    Find an opponent for a booking.
    Returns a list of potential opponents (users looking for opponents at the same time/court).
    """
    if not booking.find_opponents or booking.opponents_needed <= 0:
        return []
    
    # Find other bookings looking for opponents at the same time and court
    potential_matches = Booking.objects(
        court=booking.court,
        start_time=booking.start_time,
        end_time=booking.end_time,
        find_opponents=True,
        status__in=['pending', 'confirmed'],
        id__ne=booking.id  # Exclude current booking
    )
    
    # Filter out bookings that already have enough opponents
    candidates = []
    for match in potential_matches:
        # Check if this booking still needs opponents
        current_matches = OpponentMatch.objects(
            booking=match,
            status__in=['matched', 'accepted']
        ).count()
        
        if current_matches < match.opponents_needed:
            candidates.append(match)
    
    return candidates


def create_opponent_match(booking, opponent_booking):
    """
    Create a match between two bookings looking for opponents.
    """
    # Create match for the seeker
    match = OpponentMatch(
        booking=booking,
        seeker=booking.user,
        opponent=opponent_booking.user,
        opponents_needed=booking.opponents_needed,
        opponents_found=1,
        status='matched',
        matched_at=datetime.utcnow()
    )
    match.save()
    
    # Add opponent to booking participants
    if opponent_booking.user not in booking.participants:
        booking.participants.append(opponent_booking.user)
        booking.save()
    
    # Add seeker to opponent's booking participants
    if booking.user not in opponent_booking.participants:
        opponent_booking.participants.append(booking.user)
        opponent_booking.save()
    
    return match


def auto_match_opponents(booking):
    """
    Automatically try to match opponents for a booking.
    Returns list of created matches.
    """
    if not booking.find_opponents:
        return []
    
    candidates = find_opponent_for_booking(booking)
    matches = []
    
    opponents_still_needed = booking.opponents_needed
    
    for candidate in candidates:
        if opponents_still_needed <= 0:
            break
        
        # Create match
        match = create_opponent_match(booking, candidate)
        matches.append(match)
        opponents_still_needed -= 1
    
    return matches

