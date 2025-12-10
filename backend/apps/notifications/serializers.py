"""
Notification serializers
"""
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer"""
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'payload', 'delivered_at',
            'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

