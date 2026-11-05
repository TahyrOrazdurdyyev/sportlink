"""
Subscription Feature Permissions
"""
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from apps.subscriptions.models_user import UserSubscription


def require_feature(feature_key):
    """
    Decorator to check if user has access to a specific feature
    
    Usage:
        @api_view(['GET'])
        @permission_classes([IsAuthenticated])
        @require_feature('opponent_matching')
        def find_opponents(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            user = request.user
            
            if not user.is_authenticated:
                return Response({
                    'error': 'Authentication required'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if user has active subscription with this feature
            subscription = UserSubscription.objects(
                user=user,
                status='active',
                end_date__gte=__import__('datetime').datetime.utcnow()
            ).first()
            
            if not subscription:
                return Response({
                    'error': 'Subscription required',
                    'feature': feature_key,
                    'message': f'This feature requires an active subscription'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if not subscription.has_feature(feature_key):
                return Response({
                    'error': 'Feature not available',
                    'feature': feature_key,
                    'current_plan': subscription.plan.name,
                    'message': f'This feature is not included in your current plan'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Feature check passed
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator


def check_user_feature_access(user, feature_key):
    """
    Check if a user has access to a specific feature
    
    Returns:
        tuple: (has_access: bool, message: str)
    """
    if not user or not user.is_authenticated:
        return False, 'Authentication required'
    
    # Get active subscription
    subscription = UserSubscription.objects(
        user=user,
        status='active',
        end_date__gte=__import__('datetime').datetime.utcnow()
    ).first()
    
    if not subscription:
        return False, 'Active subscription required'
    
    if not subscription.has_feature(feature_key):
        return False, f'Feature not available in current plan'
    
    return True, 'Access granted'


def get_user_features(user):
    """
    Get all available features for a user
    
    Returns:
        dict: {feature_key: bool}
    """
    if not user or not user.is_authenticated:
        return {}
    
    subscription = UserSubscription.objects(
        user=user,
        status='active',
        end_date__gte=__import__('datetime').datetime.utcnow()
    ).first()
    
    if not subscription:
        return {}
    
    # Get plan ID from MongoDB directly to avoid dereferencing issues
    from apps.subscriptions.models import SubscriptionPlan
    
    sub_dict = subscription.to_mongo().to_dict()
    plan_id = sub_dict.get('plan')
    
    if not plan_id:
        return {}
    
    # Load plan by ID
    plan = SubscriptionPlan.objects(id=plan_id).first()
    if not plan:
        return {}
    
    return plan.features

