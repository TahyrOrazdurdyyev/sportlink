"""
Notification views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.notifications.models import Notification, PushToken
from apps.notifications.serializers import (
    NotificationSerializer,
    PushTokenSerializer,
    PushTokenCreateSerializer
)
from apps.notifications.services import register_push_token, unregister_push_token


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    """List notifications for current user"""
    notifications = Notification.objects(user=request.user).order_by('-created_at')
    serializer = NotificationSerializer([n for n in notifications], many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, pk):
    """Mark notification as read"""
    try:
        notification = Notification.objects.get(id=pk, user=request.user)
        notification.mark_as_read()
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    notifications = Notification.objects(user=request.user, is_read=False)
    count = 0
    for notification in notifications:
        notification.mark_as_read()
        count += 1
    
    return Response({
        'message': f'{count} notifications marked as read',
        'count': count
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    """Get count of unread notifications"""
    count = Notification.objects(user=request.user, is_read=False).count()
    return Response({'unread_count': count})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_token(request):
    """Register a push notification token"""
    serializer = PushTokenCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    token = serializer.validated_data['token']
    platform = serializer.validated_data['platform']
    
    push_token = register_push_token(request.user, token, platform)
    
    return Response(
        PushTokenSerializer(push_token).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unregister_token(request):
    """Unregister a push notification token"""
    token = request.data.get('token')
    
    if not token:
        return Response(
            {'error': 'Token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    unregister_push_token(token)
    
    return Response({'message': 'Token unregistered successfully'})
