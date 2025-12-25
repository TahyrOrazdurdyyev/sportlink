"""
Subscription Request Serializers
"""
from rest_framework import serializers
from apps.subscriptions.models_request import SubscriptionRequest


class SubscriptionRequestSerializer(serializers.Serializer):
    """Serializer for subscription requests"""
    id = serializers.UUIDField(read_only=True)
    user_id = serializers.SerializerMethodField()
    user_phone = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    plan_id = serializers.SerializerMethodField()
    plan_name = serializers.SerializerMethodField()
    period = serializers.CharField()
    amount = serializers.FloatField()
    status = serializers.CharField()
    user_notes = serializers.CharField(required=False, allow_blank=True)
    admin_notes = serializers.CharField(required=False, allow_blank=True)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    approved_at = serializers.DateTimeField(read_only=True)
    rejected_at = serializers.DateTimeField(read_only=True)
    
    def get_user_id(self, obj):
        try:
            # Get user_id from mongo dict to avoid DBRef issues
            user_ref = obj.to_mongo().to_dict().get('user')
            if isinstance(user_ref, str):
                return user_ref
            return str(user_ref) if user_ref else None
        except Exception as e:
            print(f"Error getting user_id: {e}")
            return None
    
    def get_user_phone(self, obj):
        try:
            from apps.users.models import User
            user_ref = obj.to_mongo().to_dict().get('user')
            if user_ref:
                user = User.objects(id=user_ref).first()
                return user.phone if user else 'Unknown'
            return 'Unknown'
        except Exception as e:
            print(f"Error getting user_phone: {e}")
            return 'Unknown'
    
    def get_user_name(self, obj):
        try:
            from apps.users.models import User
            user_ref = obj.to_mongo().to_dict().get('user')
            if user_ref:
                user = User.objects(id=user_ref).first()
                if user:
                    return f"{user.first_name or ''} {user.last_name or ''}".strip() or user.phone
            return 'Unknown'
        except Exception as e:
            print(f"Error getting user_name: {e}")
            return 'Unknown'
    
    def get_plan_id(self, obj):
        try:
            plan_ref = obj.to_mongo().to_dict().get('plan')
            if isinstance(plan_ref, str):
                return plan_ref
            return str(plan_ref) if plan_ref else None
        except Exception as e:
            print(f"Error getting plan_id: {e}")
            return None
    
    def get_plan_name(self, obj):
        try:
            from apps.subscriptions.models import SubscriptionPlan
            plan_ref = obj.to_mongo().to_dict().get('plan')
            if plan_ref:
                plan = SubscriptionPlan.objects(id=plan_ref).first()
                return plan.name.get('en', 'Unknown') if plan else 'Unknown'
            return 'Unknown'
        except Exception as e:
            print(f"Error getting plan_name: {e}")
            return 'Unknown'


class SubscriptionRequestCreateSerializer(serializers.Serializer):
    """Serializer for creating subscription request"""
    plan_id = serializers.UUIDField()
    period = serializers.ChoiceField(choices=['monthly', 'yearly'])
    user_notes = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate_plan_id(self, value):
        """Validate plan exists"""
        from apps.subscriptions.models import SubscriptionPlan
        try:
            SubscriptionPlan.objects.get(id=value)
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError("Plan not found")
        return value


class SubscriptionRequestApproveSerializer(serializers.Serializer):
    """Serializer for approving subscription request"""
    admin_notes = serializers.CharField(required=False, allow_blank=True, max_length=500)


class SubscriptionRequestRejectSerializer(serializers.Serializer):
    """Serializer for rejecting subscription request"""
    rejection_reason = serializers.CharField(required=True, max_length=500)

