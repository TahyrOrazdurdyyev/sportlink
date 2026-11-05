"""
Custom authentication backends for MongoDB
"""
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from mongoengine.errors import DoesNotExist
from apps.users.models_mongo import User


class MongoEngineBackend(BaseBackend):
    """Authentication backend for MongoEngine User model"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate user by phone/email and password"""
        if username is None or password is None:
            return None
        
        try:
            # Try to find user by phone first, then by email
            try:
                user = User.objects.get(phone=username)
            except DoesNotExist:
                user = User.objects.get(email=username)
            
            # Check password
            if user.check_password(password):
                return user
            
        except DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
        
        return None
    
    def get_user(self, user_id):
        """Get user by ID"""
        try:
            return User.objects.get(id=user_id)
        except DoesNotExist:
            return None


class FirebaseBackend(BaseBackend):
    """Authentication backend for Firebase users"""
    
    def authenticate(self, request, firebase_uid=None, **kwargs):
        """Authenticate user by Firebase UID"""
        if firebase_uid is None:
            return None
        
        try:
            user = User.objects.get(firebase_uid=firebase_uid)
            return user
        except DoesNotExist:
            return None
    
    def get_user(self, user_id):
        """Get user by ID"""
        try:
            return User.objects.get(id=user_id)
        except DoesNotExist:
            return None


class PhoneBackend(BaseBackend):
    """Authentication backend for phone-only authentication"""
    
    def authenticate(self, request, phone=None, **kwargs):
        """Authenticate user by phone only (for OTP verification)"""
        if phone is None:
            return None
        
        try:
            user = User.objects.get(phone=phone)
            return user
        except DoesNotExist:
            return None
    
    def get_user(self, user_id):
        """Get user by ID"""
        try:
            return User.objects.get(id=user_id)
        except DoesNotExist:
            return None
