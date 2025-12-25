"""
Subscription Plan views
"""
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import SubscriptionPlan, AVAILABLE_FEATURES
from .serializers import SubscriptionPlanSerializer, AvailableFeaturesSerializer


class AdminSubscriptionPlanViewSet(viewsets.ViewSet):
    """Admin CRUD for subscription plans"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List all plans"""
        plans = SubscriptionPlan.objects.all().order_by('order')
        serializer = SubscriptionPlanSerializer([self._to_dict(p) for p in plans], many=True)
        return Response({'results': serializer.data})
    
    def retrieve(self, request, pk=None):
        """Get single plan"""
        try:
            plan = SubscriptionPlan.objects.get(id=pk)
            serializer = SubscriptionPlanSerializer(self._to_dict(plan))
            return Response(serializer.data)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        """Create new plan"""
        serializer = SubscriptionPlanSerializer(data=request.data)
        if serializer.is_valid():
            plan = serializer.save()
            return Response(self._to_dict(plan), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        """Update existing plan"""
        try:
            plan = SubscriptionPlan.objects.get(id=pk)
            serializer = SubscriptionPlanSerializer(instance=self._to_dict(plan), data=request.data)
            if serializer.is_valid():
                updated_plan = serializer.update(plan, serializer.validated_data)
                return Response(self._to_dict(updated_plan))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, pk=None):
        """Delete plan"""
        try:
            plan = SubscriptionPlan.objects.get(id=pk)
            plan.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SubscriptionPlan.DoesNotExist:
            return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def _to_dict(self, plan):
        """Convert plan to dict for serializer"""
        # Calculate discounted prices
        discount_percentage = plan.discount_percentage if hasattr(plan, 'discount_percentage') else 0
        monthly_price = plan.monthly_price
        yearly_price = plan.yearly_price
        
        if discount_percentage > 0:
            discounted_monthly = monthly_price * (1 - discount_percentage / 100)
            discounted_yearly = yearly_price * (1 - discount_percentage / 100)
            has_discount = True
        else:
            discounted_monthly = monthly_price
            discounted_yearly = yearly_price
            has_discount = False
        
        return {
            'id': str(plan.id),
            'name': plan.name,
            'description': plan.description,
            'monthly_price': monthly_price,
            'yearly_price': yearly_price,
            'currency': plan.currency,
            'discount_percentage': discount_percentage,
            'discounted_monthly_price': discounted_monthly,
            'discounted_yearly_price': discounted_yearly,
            'has_discount': has_discount,
            'features': plan.features,
            'booking_limits': plan.booking_limits if hasattr(plan, 'booking_limits') else {},
            'order': plan.order,
            'is_active': plan.is_active,
            'is_popular': plan.is_popular,
            'created_at': plan.created_at,
            'updated_at': plan.updated_at,
        }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_features(request):
    """Get list of available features that can be enabled/disabled"""
    features = []
    for key, value in AVAILABLE_FEATURES.items():
        features.append({
            'key': key,
            'name': value['name'],
            'description': value['description'],
        })
    
    return Response(features)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_plans(request):
    """Get active subscription plans for mobile app (public)"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('order')
    data = []
    for plan in plans:
        # Calculate discounted prices
        discount_percentage = plan.discount_percentage if hasattr(plan, 'discount_percentage') else 0
        monthly_price = plan.monthly_price
        yearly_price = plan.yearly_price
        
        if discount_percentage > 0:
            discounted_monthly = monthly_price * (1 - discount_percentage / 100)
            discounted_yearly = yearly_price * (1 - discount_percentage / 100)
            has_discount = True
        else:
            discounted_monthly = monthly_price
            discounted_yearly = yearly_price
            has_discount = False
        
        data.append({
            'id': str(plan.id),
            'name': plan.name,
            'description': plan.description,
            'monthly_price': monthly_price,
            'yearly_price': yearly_price,
            'currency': plan.currency,
            'discount_percentage': discount_percentage,
            'discounted_monthly_price': discounted_monthly,
            'discounted_yearly_price': discounted_yearly,
            'has_discount': has_discount,
            'features': plan.features,
            'booking_limits': plan.booking_limits if hasattr(plan, 'booking_limits') else {},
            'order': plan.order,
            'is_popular': plan.is_popular,
        })
    return Response(data)

