"""
Subscription Request Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.subscriptions.models_request import SubscriptionRequest
from apps.subscriptions.models import SubscriptionPlan
from apps.subscriptions.serializers_request import (
    SubscriptionRequestSerializer,
    SubscriptionRequestCreateSerializer,
    SubscriptionRequestApproveSerializer,
    SubscriptionRequestRejectSerializer,
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_subscription_request(request):
    """Create a new subscription request"""
    serializer = SubscriptionRequestCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    plan_id = serializer.validated_data['plan_id']
    period = serializer.validated_data['period']
    user_notes = serializer.validated_data.get('user_notes', '')
    
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
        
        # Check if user already has a pending request for this plan
        existing_request = SubscriptionRequest.objects(
            user=request.user,
            plan=plan,
            status='pending'
        ).first()
        
        if existing_request:
            return Response({
                'error': 'You already have a pending request for this plan'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate amount based on period
        amount = plan.monthly_price if period == 'monthly' else plan.yearly_price
        
        # Create request
        subscription_request = SubscriptionRequest(
            user=request.user,
            plan=plan,
            period=period,
            amount=amount,
            user_notes=user_notes,
        )
        subscription_request.save()
        
        return Response(
            SubscriptionRequestSerializer(subscription_request).data,
            status=status.HTTP_201_CREATED
        )
    except SubscriptionPlan.DoesNotExist:
        return Response({
            'error': 'Plan not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_subscription_requests(request):
    """Get current user's subscription requests"""
    requests = SubscriptionRequest.objects(user=request.user).order_by('-created_at')
    serializer = SubscriptionRequestSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_subscription_requests(request):
    """Get all pending subscription requests (admin only)"""
    if not request.user.is_staff:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    requests = SubscriptionRequest.objects(status='pending').order_by('-created_at')
    serializer = SubscriptionRequestSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_subscription_requests(request):
    """Get all subscription requests (admin only)"""
    if not request.user.is_staff:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Filter by status if provided
    status_filter = request.query_params.get('status')
    
    if status_filter:
        requests = SubscriptionRequest.objects(status=status_filter).order_by('-created_at')
    else:
        requests = SubscriptionRequest.objects.all().order_by('-created_at')
    
    serializer = SubscriptionRequestSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_subscription_request(request, request_id):
    """Approve a subscription request (admin only)"""
    if not request.user.is_staff:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = SubscriptionRequestApproveSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        subscription_request = SubscriptionRequest.objects.get(id=request_id)
        
        admin_notes = serializer.validated_data.get('admin_notes', '')
        subscription = subscription_request.approve(request.user, admin_notes)
        
        return Response({
            'message': 'Subscription request approved successfully',
            'subscription_id': str(subscription.id)
        }, status=status.HTTP_200_OK)
    except SubscriptionRequest.DoesNotExist:
        return Response({
            'error': 'Request not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_subscription_request(request, request_id):
    """Reject a subscription request (admin only)"""
    if not request.user.is_staff:
        return Response({
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = SubscriptionRequestRejectSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        subscription_request = SubscriptionRequest.objects.get(id=request_id)
        
        rejection_reason = serializer.validated_data['rejection_reason']
        subscription_request.reject(request.user, rejection_reason)
        
        return Response({
            'message': 'Subscription request rejected'
        }, status=status.HTTP_200_OK)
    except SubscriptionRequest.DoesNotExist:
        return Response({
            'error': 'Request not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_subscription_request(request, request_id):
    """Cancel own subscription request"""
    try:
        subscription_request = SubscriptionRequest.objects.get(
            id=request_id,
            user=request.user
        )
        
        subscription_request.cancel()
        
        return Response({
            'message': 'Subscription request cancelled'
        }, status=status.HTTP_200_OK)
    except SubscriptionRequest.DoesNotExist:
        return Response({
            'error': 'Request not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

