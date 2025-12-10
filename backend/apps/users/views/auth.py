"""
Authentication views
"""
import firebase_admin
from firebase_admin import auth, credentials
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

# Initialize Firebase Admin SDK
firebase_initialized = False
try:
    if settings.FIREBASE_CREDENTIALS_PATH and settings.FIREBASE_PROJECT_ID:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred, {
            'projectId': settings.FIREBASE_PROJECT_ID,
        })
        firebase_initialized = True
except Exception as e:
    logger.warning(f"Firebase initialization failed: {e}")


class OTPRequestView(APIView):
    """
    Request OTP - Firebase handles SMS sending
    POST /auth/otp/request
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone = request.data.get('phone')
        
        if not phone:
            return Response(
                {'error': 'Phone number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Firebase handles OTP sending on mobile side
        # This endpoint just acknowledges the request
        # In production, you might want to track OTP requests
        
        return Response({
            'otp_sent': True,
            'message': 'OTP will be sent via Firebase'
        })


class OTPVerifyView(APIView):
    """
    Verify OTP and create/login user
    POST /auth/otp/verify
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        phone = request.data.get('phone')
        firebase_id_token = request.data.get('firebaseIdToken')
        
        if not phone or not firebase_id_token:
            return Response(
                {'error': 'Phone and firebaseIdToken are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify Firebase token
        try:
            if not firebase_initialized:
                return Response(
                    {'error': 'Firebase not configured'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            decoded_token = auth.verify_id_token(firebase_id_token)
            firebase_uid = decoded_token.get('uid')
            
            # Check if phone matches
            firebase_user = auth.get_user(firebase_uid)
            if firebase_user.phone_number != phone:
                return Response(
                    {'error': 'Phone number mismatch'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except Exception as e:
            logger.error(f"Firebase token verification failed: {e}")
            return Response(
                {'error': 'Invalid Firebase token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get or create user
        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={
                'firebase_uid': firebase_uid,
                'is_active': True,
            }
        )
        
        if not created:
            # Update Firebase UID if changed
            if user.firebase_uid != firebase_uid:
                user.firebase_uid = firebase_uid
                user.save()
        
        # Update last active
        user.last_active_at = timezone.now()
        user.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        from apps.users.serializers import UserSerializer
        user_serializer = UserSerializer(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_serializer.data,
            'created': created
        })

