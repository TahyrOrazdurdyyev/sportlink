"""
User Subscription Views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.subscriptions.models import SubscriptionPlan
from apps.subscriptions.models_user import UserSubscription
from apps.subscriptions.permissions import get_user_features
from datetime import datetime, timedelta


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_subscription(request):
    """Get current user's subscription status"""
    user = request.user
    
    # Get active subscription
    subscription = UserSubscription.objects(
        user=user,
        status='active',
        end_date__gte=datetime.utcnow()
    ).first()
    
    if not subscription:
        return Response({
            'has_subscription': False,
            'message': 'No active subscription',
            'available_plans': _get_available_plans()
        })
    
    return Response({
        'has_subscription': True,
        'subscription': {
            'id': str(subscription.id),
            'plan': {
                'id': str(subscription.plan.id),
                'name': subscription.plan.name,
                'description': subscription.plan.description,
            },
            'start_date': subscription.start_date.isoformat(),
            'end_date': subscription.end_date.isoformat(),
            'status': subscription.status,
            'is_auto_renew': subscription.is_auto_renew,
            'features': subscription.plan.features,
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe(request):
    """
    Subscribe to a plan
    
    Body:
    - plan_id: UUID
    - period: 'monthly' or 'yearly'
    - payment_method: str
    - transaction_id: str (optional)
    """
    user = request.user
    plan_id = request.data.get('plan_id')
    period = request.data.get('period', 'monthly')
    payment_method = request.data.get('payment_method', 'card')
    transaction_id = request.data.get('transaction_id', '')
    
    if not plan_id:
        return Response({
            'error': 'plan_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
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
        return Response({
            'error': 'You already have an active subscription',
            'current_subscription': {
                'plan': existing.plan.name,
                'end_date': existing.end_date.isoformat()
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate dates and amount
    start_date = datetime.utcnow()
    if period == 'yearly':
        end_date = start_date + timedelta(days=365)
        amount = plan.yearly_price
    else:  # monthly
        end_date = start_date + timedelta(days=30)
        amount = plan.monthly_price
    
    # Create subscription
    subscription = UserSubscription(
        user=user,
        plan=plan,
        start_date=start_date,
        end_date=end_date,
        status='active',
        amount_paid=amount,
        payment_method=payment_method,
        transaction_id=transaction_id,
    )
    subscription.save()
    
    return Response({
        'success': True,
        'message': 'Subscription activated successfully',
        'subscription': {
            'id': str(subscription.id),
            'plan': plan.name,
            'start_date': subscription.start_date.isoformat(),
            'end_date': subscription.end_date.isoformat(),
            'amount_paid': amount,
            'features': plan.features,
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """Cancel current subscription"""
    user = request.user
    
    subscription = UserSubscription.objects(
        user=user,
        status='active'
    ).first()
    
    if not subscription:
        return Response({
            'error': 'No active subscription found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    subscription.cancel()
    
    return Response({
        'success': True,
        'message': 'Subscription cancelled successfully',
        'cancelled_at': subscription.cancelled_at.isoformat() if subscription.cancelled_at else None
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_features(request):
    """Get user's available features"""
    user = request.user
    features = get_user_features(user)
    
    return Response({
        'features': features,
        'has_subscription': bool(features)
    })


def _get_available_plans():
    """Helper to get available plans list"""
    plans = SubscriptionPlan.objects(is_active=True).order_by('order')
    return [
        {
            'id': str(plan.id),
            'name': plan.name,
            'description': plan.description,
            'monthly_price': plan.monthly_price,
            'yearly_price': plan.yearly_price,
            'currency': plan.currency,
            'is_popular': plan.is_popular,
        } for plan in plans
    ]

