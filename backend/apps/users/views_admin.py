"""
Admin authentication views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from apps.users.models import User
from apps.core.jwt_mongo_auth import create_jwt_token_for_user


@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    """
    Admin login with phone/email and password
    """
    username = request.data.get('username')  # Can be phone or email
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Try to find user by phone or email
    user = None
    try:
        if '@' in username:
            user = User.objects.get(email=username)
        else:
            user = User.objects.get(phone=username)
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Check if user is staff
    if not user.is_staff and not user.is_superuser:
        return Response(
            {'error': 'Access denied. Admin privileges required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Verify password
    if not user.check_password(password):
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generate JWT tokens
    tokens = create_jwt_token_for_user(user)
    
    return Response({
        'token': tokens['access'],
        'refresh': tokens['refresh'],
        'user': {
            'id': str(user.id),
            'phone': user.phone,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
    })

