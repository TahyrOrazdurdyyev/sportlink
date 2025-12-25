"""
User views for MongoDB - SIMPLIFIED VERSION
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.core.mongoengine_drf import MongoEngineModelViewSet, GeoQueryMixin
from apps.users.models import User
from apps.users.serializers import (
    UserSerializer, UserPublicSerializer, UserCreateSerializer, UserUpdateSerializer, AdminUserSerializer
)


# Auth views - Register & Login
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user
    Required: first_name, last_name, nickname, phone, password
    """
    import re
    
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    nickname = request.data.get('nickname')
    phone = request.data.get('phone')
    password = request.data.get('password')
    fcm_token = request.data.get('fcm_token')
    
    # Validation
    if not all([first_name, last_name, nickname, phone, password]):
        return Response({
            'error': 'All fields are required: first_name, last_name, nickname, phone, password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate password strength
    if len(password) < 8:
        return Response({
            'error': 'Password must be at least 8 characters long'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not re.search(r'[a-zA-Z]', password):
        return Response({
            'error': 'Password must contain at least one letter'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not re.search(r'\d', password):
        return Response({
            'error': 'Password must contain at least one number'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return Response({
            'error': 'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if nickname already exists
    if User.objects(nickname=nickname).first():
        return Response({
            'error': 'Nickname already taken'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if phone already exists
    if User.objects(phone=phone).first():
        return Response({
            'error': 'Phone number already registered'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create user
    user = User(
        first_name=first_name,
        last_name=last_name,
        nickname=nickname,
        phone=phone,
        fcm_token=fcm_token
    )
    user.set_password(password)
    user.save()
    
    # Generate JWT tokens
    from apps.core.jwt_mongo_auth import create_jwt_token_for_user
    tokens = create_jwt_token_for_user(user)
    
    return Response({
        'access': tokens['access'],
        'refresh': tokens['refresh'],
        'user': UserSerializer(user).data,
        'message': 'Registration successful'
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user
    Required: identifier (phone or nickname), password
    """
    login_value = request.data.get('identifier') or request.data.get('login')  # Can be phone or nickname
    password = request.data.get('password')
    fcm_token = request.data.get('fcm_token')
    
    if not login_value or not password:
        return Response({
            'error': 'Identifier (phone or nickname) and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Try to find user by phone or nickname
    user = User.objects(phone=login_value).first() or User.objects(nickname=login_value).first()
    
    if not user:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check password
    if not user.check_password(password):
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if user is active
    if not user.is_active:
        return Response({
            'error': 'Account is disabled'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Update FCM token if provided
    if fcm_token:
        user.fcm_token = fcm_token
        user.save()
    
    # Generate JWT tokens
    from apps.core.jwt_mongo_auth import create_jwt_token_for_user
    tokens = create_jwt_token_for_user(user)
    
    return Response({
        'access': tokens['access'],
        'refresh': tokens['refresh'],
        'user': UserSerializer(user).data,
        'message': 'Login successful'
    })


# User profile views
class UserViewSet(MongoEngineModelViewSet):
    """User CRUD operations"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.all()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_fcm_token(request):
    """Update user's FCM token for push notifications"""
    fcm_token = request.data.get('fcm_token')
    
    if not fcm_token:
        return Response({'error': 'FCM token required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    user.fcm_token = fcm_token
    user.save()
    
    return Response({'message': 'FCM token updated successfully'})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update current user profile"""
    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(UserSerializer(request.user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password"""
    import re
    
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    # Validation
    if not old_password or not new_password:
        return Response({
            'error': 'Both old_password and new_password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check old password
    user = request.user
    if not user.check_password(old_password):
        return Response({
            'error': 'Current password is incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate new password strength
    if len(new_password) < 8:
        return Response({
            'error': 'Password must be at least 8 characters long'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not re.search(r'[a-zA-Z]', new_password):
        return Response({
            'error': 'Password must contain at least one letter'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not re.search(r'\d', new_password):
        return Response({
            'error': 'Password must contain at least one number'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
        return Response({
            'error': 'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if new password is same as old
    if old_password == new_password:
        return Response({
            'error': 'New password must be different from current password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Update password
    user.set_password(new_password)
    user.save()
    
    return Response({
        'message': 'Password changed successfully'
    }, status=status.HTTP_200_OK)


# Partner search
class SearchPartnersView(APIView, GeoQueryMixin):
    """Search for partners with geo-location"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get query parameters
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius_km = float(request.query_params.get('radius_km', 10.0))
        
        # Base queryset (exclude current user)
        queryset = User.objects.filter(id__ne=request.user.id, is_active=True)
        
        # Filter by location if provided
        if lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                queryset = self.filter_by_location(queryset, lat, lng, radius_km)
            except (ValueError, TypeError):
                pass
        
        # Limit results
        users = list(queryset[:50])
        
        serializer = UserPublicSerializer(users, many=True)
        return Response(serializer.data)


# Admin views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_list_users(request):
    """List all users with subscription info"""
    users = User.objects.all().order_by('-created_at')
    serializer = AdminUserSerializer(users, many=True)
    data = serializer.data
    
    # Debug output
    print(f"\n{'='*80}")
    print(f"ADMIN LIST USERS - Serialized {len(data)} users")
    print(f"{'='*80}")
    for user_data in data:
        print(f"User: {user_data.get('phone')}")
        print(f"  nickname: {user_data.get('nickname')}")
        print(f"  first_name: {user_data.get('first_name')}")
        print(f"  last_name: {user_data.get('last_name')}")
        print(f"  subscription_plan: {user_data.get('subscription_plan')}")
        print(f"  subscription_end_date: {user_data.get('subscription_end_date')}")
        print(f"  subscription_status: {user_data.get('subscription_status')}")
    print(f"{'='*80}\n")
    
    return Response(data)
