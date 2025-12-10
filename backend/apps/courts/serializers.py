"""
Court serializers for MongoDB
"""
from rest_framework import serializers
from apps.core.mongoengine_drf import MongoEngineModelSerializer
from apps.courts.models import Court


class CourtSerializer(MongoEngineModelSerializer):
    """Full court serializer"""
    location = serializers.ListField(
        child=serializers.FloatField(),
        required=False
    )
    
    class Meta:
        model = Court
        fields = [
            'id', 'name_i18n', 'address', 'location', 'type', 'owner',
            'attributes', 'images', 'tariffs', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create court with location handling"""
        # Handle location (convert from [lng, lat] to GeoJSON Point)
        location = validated_data.pop('location', None)
        if location and len(location) == 2:
            validated_data['location'] = {
                'type': 'Point',
                'coordinates': [float(location[0]), float(location[1])]
            }
        
        return super().create(validated_data)


class CourtListSerializer(MongoEngineModelSerializer):
    """Court list serializer (minimal fields)"""
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = Court
        fields = [
            'id', 'name_i18n', 'address', 'type', 'images',
            'is_active', 'distance'
        ]
    
    def get_distance(self, obj):
        """Calculate distance from user location"""
        # Distance will be calculated in the view
        return getattr(obj, '_distance', None)


class CourtDetailSerializer(MongoEngineModelSerializer):
    """Detailed court serializer"""
    availability = serializers.SerializerMethodField()
    
    class Meta:
        model = Court
        fields = [
            'id', 'name_i18n', 'address', 'location', 'type', 'owner',
            'attributes', 'images', 'tariffs', 'availability',
            'is_active', 'created_at'
        ]
    
    def get_availability(self, obj):
        """Get today's availability"""
        from datetime import date
        today = date.today()
        slots = obj.get_availability_for_date(today)
        return [
            {
                'start_time': slot.start_time.isoformat(),
                'end_time': slot.end_time.isoformat(),
                'status': slot.status
            }
            for slot in slots
        ]
