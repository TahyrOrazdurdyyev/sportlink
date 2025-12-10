"""
Tournament models for MongoDB
"""
import uuid
from datetime import datetime
from mongoengine import Document, EmbeddedDocument, fields
from apps.users.models import User
from apps.courts.models import Court


class TournamentParticipant(EmbeddedDocument):
    """Embedded tournament participant"""
    user = fields.ReferenceField(User, required=True)
    status = fields.StringField(
        choices=['applied', 'accepted', 'rejected', 'paid', 'participated'],
        default='applied'
    )
    registration_date = fields.DateTimeField(default=datetime.utcnow)
    payment_status = fields.StringField(
        choices=['pending', 'paid', 'refunded'],
        default='pending'
    )
    notes = fields.StringField(max_length=500)


class Tournament(Document):
    """Tournament model for MongoDB"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('open', 'Registration Open'),
        ('closed', 'Registration Closed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # ID
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    
    # Basic info
    name_i18n = fields.DictField(default=dict)  # Multilingual name
    description_i18n = fields.DictField(default=dict)  # Multilingual description
    
    # Venue
    courts = fields.ListField(fields.ReferenceField(Court))
    location_description = fields.StringField()  # Additional location info
    
    # Organizer
    organizer_info = fields.DictField(default=dict)  # Contact info, etc.
    created_by = fields.ReferenceField(User, required=True, reverse_delete_rule=2)  # NULLIFY
    
    # Schedule
    start_date = fields.DateTimeField(required=True)
    end_date = fields.DateTimeField(required=True)
    registration_deadline = fields.DateTimeField()
    
    # Capacity
    max_participants = fields.IntField(min_value=1, required=True)
    min_participants = fields.IntField(min_value=1, default=2)
    
    # Registration
    registration_open = fields.BooleanField(default=True)
    registration_link = fields.URLField()  # External registration link (optional)
    registration_fee = fields.DecimalField(min_value=0, precision=2, default=0)
    
    # Participants
    participants = fields.ListField(fields.EmbeddedDocumentField(TournamentParticipant))
    
    # Status
    status = fields.StringField(choices=STATUS_CHOICES, default='draft')
    
    # Additional info
    rules = fields.StringField()
    prizes = fields.DictField()  # Prize structure
    categories = fields.ListField(fields.StringField())  # Age groups, skill levels, etc.
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'tournaments',
        'indexes': [
            'created_by',
            'status',
            'start_date',
            'end_date',
            'registration_deadline',
            'registration_open',
            'created_at',
            [('start_date', 1), ('status', 1)],  # Compound index for active tournaments
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
    
    def get_description(self, language='tk'):
        """Get description in specified language"""
        return self.description_i18n.get(language, self.description_i18n.get('tk', ''))
    
    def get_participant_count(self):
        """Get number of participants"""
        return len([p for p in self.participants if p.status in ['accepted', 'paid', 'participated']])
    
    def is_full(self):
        """Check if tournament is full"""
        return self.get_participant_count() >= self.max_participants
    
    def can_register(self):
        """Check if registration is open"""
        now = datetime.utcnow()
        return (
            self.registration_open and
            self.status == 'open' and
            not self.is_full() and
            (not self.registration_deadline or now < self.registration_deadline)
        )
    
    def add_participant(self, user):
        """Add participant to tournament"""
        if not self.can_register():
            raise ValueError("Registration is not available")
        
        # Check if user is already registered
        for participant in self.participants:
            if participant.user.id == user.id:
                raise ValueError("User is already registered")
        
        participant = TournamentParticipant(user=user)
        self.participants.append(participant)
        self.save()
        
        return participant
    
    def close_registration(self):
        """Close tournament registration"""
        self.registration_open = False
        if self.status == 'open':
            self.status = 'closed'
        self.save()
