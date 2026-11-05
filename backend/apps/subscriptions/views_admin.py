"""
Admin Subscription Views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.subscriptions.models import SubscriptionPlan
from apps.subscriptions.models_user import UserSubscription
from apps.users.models import User
from datetime import datetime, timedelta


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_manual_subscription(request):
    """
    Manually create subscription for a user (admin only)
    
    Body:
    - user_id: UUID
    - plan_id: UUID
    - duration_days: int (custom duration in days)
    - notes: str (optional)
    """
    if not request.user.is_staff:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    plan_id = request.data.get('plan_id')
    duration_days = request.data.get('duration_days')
    notes = request.data.get('notes', '')
    
    # Validation
    if not all([user_id, plan_id, duration_days]):
        return Response({
            'error': 'user_id, plan_id, and duration_days are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        duration_days = int(duration_days)
        if duration_days <= 0:
            raise ValueError("Duration must be positive")
    except ValueError as e:
        return Response({
            'error': f'Invalid duration_days: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get user and plan
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
    except SubscriptionPlan.DoesNotExist:
        return Response({
            'error': 'Plan not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check for existing active subscription
    existing = UserSubscription.objects(
        user=user,
        status='active',
        end_date__gte=datetime.utcnow()
    ).first()
    
    if existing:
        # Cancel existing subscription
        existing.cancel()
    
    # Calculate dates
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=duration_days)
    
    # Calculate amount based on duration
    # Use monthly price as base and calculate proportionally
    days_in_month = 30
    amount = (plan.monthly_price / days_in_month) * duration_days
    
    # Create subscription
    subscription = UserSubscription(
        user=user,
        plan=plan,
        start_date=start_date,
        end_date=end_date,
        status='active',
        amount_paid=amount,
        payment_method='manual',
        transaction_id=f'MANUAL_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}',
    )
    subscription.save()
    
    return Response({
        'success': True,
        'message': f'Subscription created for {user.phone}',
        'subscription': {
            'id': str(subscription.id),
            'user': {
                'id': str(user.id),
                'phone': user.phone,
                'name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
            },
            'plan': {
                'id': str(plan.id),
                'name': plan.name,
            },
            'start_date': subscription.start_date.isoformat(),
            'end_date': subscription.end_date.isoformat(),
            'duration_days': duration_days,
            'amount_paid': float(amount),
            'status': subscription.status,
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_subscription(request, user_id):
    """Get user's current subscription (admin only)"""
    if not request.user.is_staff:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get active subscription
    subscription = UserSubscription.objects(
        user=user,
        status='active',
        end_date__gte=datetime.utcnow()
    ).first()
    
    if not subscription:
        return Response({
            'has_subscription': False,
            'message': 'No active subscription'
        })
    
    return Response({
        'has_subscription': True,
        'subscription': {
            'id': str(subscription.id),
            'plan': {
                'id': str(subscription.plan.id),
                'name': subscription.plan.name,
            },
            'start_date': subscription.start_date.isoformat(),
            'end_date': subscription.end_date.isoformat(),
            'status': subscription.status,
            'amount_paid': float(subscription.amount_paid),
            'payment_method': subscription.payment_method,
            'features': subscription.plan.features,
        }
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_user_subscription(request, user_id):
    """Cancel user's subscription (admin only)"""
    if not request.user.is_staff:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    subscription = UserSubscription.objects(
        user=user,
        status='active'
    ).first()
    
    if not subscription:
        return Response({
            'error': 'No active subscription found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    print(f"DEBUG: Cancelling subscription {subscription.id} for user {user.phone}")
    print(f"DEBUG: Status before cancel: {subscription.status}")
    subscription.cancel()
    print(f"DEBUG: Status after cancel: {subscription.status}")
    
    return Response({
        'success': True,
        'message': 'Subscription cancelled successfully'
    })

