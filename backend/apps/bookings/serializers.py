"""
Booking serializers for MongoDB
"""
from rest_framework import serializers
from apps.core.mongoengine_drf import MongoEngineModelSerializer
from apps.bookings.models import Booking
from apps.users.serializers import UserPublicSerializer
from apps.courts.serializers import CourtListSerializer


class BookingSerializer(MongoEngineModelSerializer):
    """Full booking serializer"""
    user_details = UserPublicSerializer(source='user', read_only=True)
    court_details = CourtListSerializer(source='court', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'court', 'start_time', 'end_time', 'status',
            'participants', 'tariff_snapshot', 'total_price',
            'payment_method', 'payment_status', 'notes',
            'created_at', 'updated_at', 'user_details', 'court_details'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate booking data"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError("End time must be after start time")
        
        return data


class BookingCreateSerializer(MongoEngineModelSerializer):
    """Serializer for creating bookings"""
    
    class Meta:
        model = Booking
        fields = [
            'court', 'start_time', 'end_time', 'participants',
            'payment_method', 'notes'
        ]
    
    def create(self, validated_data):
        """Create booking with user from request"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
        
        return super().create(validated_data)


class BookingListSerializer(MongoEngineModelSerializer):
    """Booking list serializer (minimal fields)"""
    court_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'court_name', 'start_time', 'end_time', 'status',
            'payment_status', 'created_at'
        ]
    
    def get_court_name(self, obj):
        """Get court name in default language"""
        if obj.court and obj.court.name_i18n:
            return obj.court.get_name()
        return ""
