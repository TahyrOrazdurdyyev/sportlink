"""
User models for MongoDB
"""
import uuid
from datetime import datetime
from mongoengine import Document, EmbeddedDocument, fields
from django.contrib.auth.hashers import make_password, check_password


class UserCategory(EmbeddedDocument):
    """Embedded category for user interests with experience level"""
    category_id = fields.UUIDField(required=True)  # Changed to UUID to match Category model
    experience_level = fields.IntField(min_value=1, max_value=10, default=1)  # Experience for this specific sport
    
    
class User(Document):
    """User model for MongoDB"""
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    # ID
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4, binary=False)
    
    # Authentication
    phone = fields.StringField(max_length=20, required=True, unique=True)
    nickname = fields.StringField(max_length=50, unique=True, sparse=True)  # Unique username
    email = fields.EmailField(unique=True, sparse=True)  # sparse allows multiple null values
    password = fields.StringField(max_length=128)  # For Django compatibility
    
    # Personal info
    first_name = fields.StringField(max_length=150)
    last_name = fields.StringField(max_length=150)
    birth_date = fields.DateTimeField()  # Store as datetime for age calculation
    age = fields.IntField(min_value=1, max_value=120)  # Optional: can be calculated from birth_date
    gender = fields.StringField(max_length=10, choices=GENDER_CHOICES)
    
    # Location
    city = fields.StringField(max_length=100)
    location = fields.PointField()  # MongoDB 2dsphere GeoJSON point
    
    # Sports profile
    categories = fields.ListField(fields.EmbeddedDocumentField(UserCategory))  # Legacy field for backward compatibility
    favorite_sports = fields.ListField(fields.EmbeddedDocumentField(UserCategory))  # List of favorite sports with experience levels
    experience_level = fields.IntField(min_value=1, max_value=7, default=1)  # Keep for backward compatibility
    preferred_ball = fields.StringField(max_length=100)
    goals = fields.ListField(fields.StringField(max_length=50))  # ["find_partner", "book_court", etc.]
    
    # Rating
    rating = fields.FloatField(default=0.0)
    
    # Profile image
    avatar_url = fields.StringField()  # Can be relative or absolute URL
    
    # Status
    is_active = fields.BooleanField(default=True)
    is_banned = fields.BooleanField(default=False)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    last_active_at = fields.DateTimeField()
    
    # Firebase
    firebase_uid = fields.StringField(max_length=128, unique=True, sparse=True)
    fcm_token = fields.StringField()
    
    # Django authentication compatibility
    last_login = fields.DateTimeField()
    
    meta = {
        'collection': 'users',
        'indexes': [
            'phone',
            'nickname',
            'email',
            'firebase_uid',
            'location',  # 2dsphere index for geo queries
            'created_at',
            'last_active_at',
        ]
    }
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.phone
    
    def save(self, *args, **kwargs):
        """Override save to update timestamps and migrate legacy data"""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Migrate legacy categories to favorite_sports if needed
        if self.categories and not self.favorite_sports:
            self.favorite_sports = self.categories
        
        return super().save(*args, **kwargs)
    
    def set_password(self, raw_password):
        """Set password using Django's password hasher"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check password using Django's password hasher"""
        return check_password(raw_password, self.password)
    
    # Django User model compatibility methods
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser
    
    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_authenticated(self):
        return True
