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
    UserSerializer, UserPublicSerializer, UserCreateSerializer, UserUpdateSerializer
)


# Simple auth views
@api_view(['POST'])
@permission_classes([AllowAny])
def otp_request(request):
    """Request OTP for phone number"""
    phone = request.data.get('phone')
    if not phone:
        return Response({'error': 'Phone number required'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'otp_sent': True, 'message': 'OTP would be sent via Firebase'})


@api_view(['POST'])
@permission_classes([AllowAny])
def otp_verify(request):
    """Verify OTP and create/login user"""
    phone = request.data.get('phone')
    otp = request.data.get('otp')
    
    if not phone or not otp:
        return Response({'error': 'Phone and OTP required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Get or create user
    try:
        user = User.objects.get(phone=phone)
    except User.DoesNotExist:
        user = User(phone=phone)
        user.save()
    
    # Generate JWT tokens for MongoDB user
    from apps.core.jwt_mongo_auth import create_jwt_token_for_user
    tokens = create_jwt_token_for_user(user)
    
    return Response({
        'access': tokens['access'],
        'refresh': tokens['refresh'],
        'user': UserSerializer(user).data
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


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update current user profile"""
    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(UserSerializer(request.user).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


