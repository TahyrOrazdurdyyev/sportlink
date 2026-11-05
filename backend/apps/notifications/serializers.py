"""
Notification serializers
"""
from rest_framework import serializers
from apps.notifications.models import Notification, PushToken


class NotificationSerializer(serializers.Serializer):
    """Serializer for notifications"""
    id = serializers.CharField(read_only=True)
    type = serializers.CharField()
    title = serializers.DictField()
    message = serializers.DictField()
    data = serializers.DictField(required=False)
    is_read = serializers.BooleanField()
    is_sent = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    read_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)


class PushTokenSerializer(serializers.Serializer):
    """Serializer for push tokens"""
    id = serializers.CharField(read_only=True)
    token = serializers.CharField()
    platform = serializers.CharField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)


class PushTokenCreateSerializer(serializers.Serializer):
    """Serializer for creating/updating push tokens"""
    token = serializers.CharField(required=True, max_length=500)
    platform = serializers.ChoiceField(choices=['ios', 'android', 'web'], required=True)
