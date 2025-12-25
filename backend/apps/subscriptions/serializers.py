"""
Subscription Plan serializers
"""
from rest_framework import serializers
from .models import SubscriptionPlan, AVAILABLE_FEATURES


class SubscriptionPlanSerializer(serializers.Serializer):
    """Serializer for Subscription Plans"""
    id = serializers.CharField(read_only=True)
    name = serializers.DictField()
    description = serializers.DictField(required=False)
    monthly_price = serializers.FloatField()
    yearly_price = serializers.FloatField()
    currency = serializers.CharField(default='TMT')
    discount_percentage = serializers.FloatField(default=0.0, min_value=0.0, max_value=100.0)
    features = serializers.DictField()
    booking_limits = serializers.DictField(required=False, default=dict)
    order = serializers.IntegerField(default=0)
    is_active = serializers.BooleanField(default=True)
    is_popular = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return SubscriptionPlan.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class AvailableFeaturesSerializer(serializers.Serializer):
    """Serializer for available features list"""
    key = serializers.CharField()
    name = serializers.DictField()
    description = serializers.DictField()

