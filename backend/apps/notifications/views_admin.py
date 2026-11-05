"""
Admin views for notifications
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.users.models import User
from apps.notifications.fcm_utils import send_push_notification, send_push_notification_multicast
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_admin_notification(request):
    """Send push notification from admin panel"""
    # Check if user is staff
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    title = request.data.get('title')
    body = request.data.get('body')
    notification_type = request.data.get('type', 'all')  # 'all', 'specific', 'test'
    user_ids = request.data.get('user_ids', [])
    test_token = request.data.get('test_token')
    
    if not title or not body:
        return Response(
            {'error': 'Title and body are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        if notification_type == 'test' and test_token:
            # Send test notification
            success = send_push_notification(
                token=test_token,
                title=title,
                body=body,
                data={'type': 'admin_test'},
            )
            return Response({
                'success': success,
                'message': 'Test notification sent' if success else 'Failed to send test notification',
                'sent_count': 1 if success else 0,
            })
        
        elif notification_type == 'specific' and user_ids:
            # Send to specific users
            users = User.objects.filter(
                id__in=user_ids,
                fcm_token__exists=True,
                fcm_token__ne=''
            )
            tokens = [user.fcm_token for user in users]
            
            if not tokens:
                return Response(
                    {'error': 'No users with FCM tokens found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = send_push_notification_multicast(
                tokens=tokens,
                title=title,
                body=body,
                data={'type': 'admin_notification'},
            )
            
            return Response({
                'success': True,
                'sent_count': result['success'],
                'failed_count': result['failure'],
                'message': f"Sent to {result['success']} users",
            })
        
        elif notification_type == 'all':
            # Send to all active users
            users = User.objects.filter(
                is_active=True,
                fcm_token__exists=True,
                fcm_token__ne=''
            )
            tokens = [user.fcm_token for user in users]
            
            if not tokens:
                return Response(
                    {'error': 'No active users with FCM tokens found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Send in batches
            batch_size = 500
            total_success = 0
            total_failure = 0
            
            for i in range(0, len(tokens), batch_size):
                batch_tokens = tokens[i:i + batch_size]
                result = send_push_notification_multicast(
                    tokens=batch_tokens,
                    title=title,
                    body=body,
                    data={'type': 'admin_broadcast'},
                )
                total_success += result['success']
                total_failure += result['failure']
            
            return Response({
                'success': True,
                'sent_count': total_success,
                'failed_count': total_failure,
                'total_users': len(tokens),
                'message': f"Broadcast sent to {total_success} users",
            })
        
        else:
            return Response(
                {'error': 'Invalid notification type or missing parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        logger.error(f'Error sending admin notification: {e}')
        return Response(
            {'error': f'Failed to send notification: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notification_stats(request):
    """Get notification statistics"""
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        total_users = User.objects.filter(is_active=True).count()
        users_with_tokens = User.objects.filter(
            is_active=True,
            fcm_token__exists=True,
            fcm_token__ne=''
        ).count()
        
        return Response({
            'total_users': total_users,
            'users_with_tokens': users_with_tokens,
            'users_without_tokens': total_users - users_with_tokens,
        })
    
    except Exception as e:
        logger.error(f'Error getting notification stats: {e}')
        return Response(
            {'error': f'Failed to get stats: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

