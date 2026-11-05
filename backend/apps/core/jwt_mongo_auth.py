"""
Custom JWT authentication for MongoDB User
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from apps.users.models import User


class MongoJWTAuthentication(JWTAuthentication):
    """JWT Authentication for MongoDB User"""
    
    def get_user(self, validated_token):
        """Get MongoDB User from JWT token"""
        try:
            user_id = validated_token.get('user_id')
            if not user_id:
                return None
                
            # Get user from MongoDB
            user = User.objects.get(id=user_id)
            return user
            
        except (User.DoesNotExist, ValueError, TypeError):
            return None
    
    def authenticate(self, request):
        """Authenticate request with JWT token"""
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        
        if user is None:
            return None
            
        return (user, validated_token)


class MongoUser:
    """Wrapper to make MongoDB User compatible with Django auth"""
    
    def __init__(self, mongo_user):
        self.mongo_user = mongo_user
        
    @property
    def id(self):
        return str(self.mongo_user.id)
    
    @property
    def pk(self):
        return str(self.mongo_user.id)
    
    @property
    def username(self):
        return self.mongo_user.phone
    
    @property
    def email(self):
        return self.mongo_user.email
    
    @property
    def first_name(self):
        return self.mongo_user.first_name
    
    @property
    def last_name(self):
        return self.mongo_user.last_name
    
    @property
    def is_active(self):
        return self.mongo_user.is_active
    
    @property
    def is_staff(self):
        return self.mongo_user.is_staff
    
    @property
    def is_superuser(self):
        return self.mongo_user.is_superuser
    
    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_authenticated(self):
        return True
    
    def __str__(self):
        return str(self.mongo_user)
    
    def __getattr__(self, name):
        """Delegate other attributes to mongo_user"""
        return getattr(self.mongo_user, name)


def create_jwt_token_for_user(user):
    """Create JWT tokens for MongoDB user"""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    # Create a wrapper for Django compatibility
    django_user = MongoUser(user)
    
    # Create token
    refresh = RefreshToken()
    refresh['user_id'] = str(user.id)
    refresh['phone'] = user.phone
    refresh['email'] = user.email or ""
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


