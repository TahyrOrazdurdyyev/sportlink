"""
User serializers for MongoDB
"""
from rest_framework import serializers
from apps.core.mongoengine_drf import MongoEngineModelSerializer
from apps.users.models import User
from apps.categories.models import Category


class UserSerializer(MongoEngineModelSerializer):
    """Full user serializer"""
    
    class Meta:
        model = User
        fields = [
            'id', 'phone', 'email', 'first_name', 'last_name', 'birth_date',
            'gender', 'city', 'location', 'categories', 'experience_level',
            'preferred_ball', 'goals', 'rating', 'avatar_url', 'is_active',
            'created_at', 'updated_at', 'last_active_at'
        ]
        read_only_fields = ['id', 'rating', 'created_at', 'updated_at']


class UserPublicSerializer(MongoEngineModelSerializer):
    """Public user profile serializer (limited fields)"""
    
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'city', 'experience_level',
            'rating', 'avatar_url', 'last_active_at'
        ]


class UserCreateSerializer(MongoEngineModelSerializer):
    """Serializer for user creation"""
    
    class Meta:
        model = User
        fields = [
            'phone', 'email', 'first_name', 'last_name', 'birth_date',
            'gender', 'city', 'firebase_uid'
        ]
    
    def create(self, validated_data):
        """Create user with Firebase UID"""
        user = User(**validated_data)
        user.save()
        return user


class UserUpdateSerializer(MongoEngineModelSerializer):
    """Serializer for updating user profile"""
    location = serializers.ListField(
        child=serializers.FloatField(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'birth_date', 'gender',
            'city', 'location', 'categories', 'experience_level',
            'preferred_ball', 'goals', 'avatar_url'
        ]
    
    def update(self, instance, validated_data):
        """Update user with location handling"""
        # Handle location (convert from [lng, lat] to GeoJSON Point)
        location = validated_data.pop('location', None)
        if location is not None and len(location) == 2:
            validated_data['location'] = {
                'type': 'Point',
                'coordinates': [float(location[0]), float(location[1])]
            }
        
        return super().update(instance, validated_data)
