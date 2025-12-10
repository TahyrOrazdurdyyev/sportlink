"""
User profile views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils import timezone
from .serializers import UserSerializer, UserUpdateSerializer, UserPublicSerializer

User = get_user_model()


class UserProfileView(APIView):
    """
    Get and update current user profile
    GET /users/me/
    PATCH /users/me/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Update last active
            request.user.last_active_at = timezone.now()
            request.user.save()
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPublicView(APIView):
    """
    Get public user profile
    GET /users/{id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, is_active=True, is_banned=False)
            serializer = UserPublicSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

