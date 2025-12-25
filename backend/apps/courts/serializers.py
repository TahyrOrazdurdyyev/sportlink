"""
Court serializers for MongoDB
"""
from rest_framework import serializers
from apps.core.mongoengine_drf import MongoEngineModelSerializer
from apps.courts.models import Court


class CourtSerializer(MongoEngineModelSerializer):
    """Full court serializer for admin"""
    id = serializers.UUIDField(read_only=True)
    location = serializers.ListField(
        child=serializers.FloatField(),
        required=False,
        allow_null=True,
        help_text="Location as [longitude, latitude]"
    )
    owner_id = serializers.UUIDField(required=False, allow_null=True)
    
    class Meta:
        model = Court
        fields = [
            'id', 'name_i18n', 'address', 'location', 'type', 
            'owner_id', 'attributes', 'images', 'tariffs', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Convert location from GeoJSON to [lng, lat]"""
        ret = super().to_representation(instance)
        if instance.location and 'coordinates' in instance.location:
            ret['location'] = instance.location['coordinates']
        # Ensure is_active is boolean
        ret['is_active'] = bool(instance.is_active)
        
        # Convert relative image URLs to absolute URLs
        if ret.get('images'):
            request = self.context.get('request')
            absolute_images = []
            for img_url in ret['images']:
                if img_url and not img_url.startswith('http'):
                    # It's a relative URL, make it absolute
                    if request:
                        absolute_url = request.build_absolute_uri(img_url)
                        absolute_images.append(absolute_url)
                    else:
                        # Fallback if no request in context
                        from django.conf import settings
                        base_url = getattr(settings, 'BASE_URL', 'http://192.168.31.106:8000')
                        absolute_images.append(f"{base_url}{img_url}")
                else:
                    absolute_images.append(img_url)
            ret['images'] = absolute_images
        
        return ret
    
    def create(self, validated_data):
        """Create court with location handling"""
        location = validated_data.pop('location', None)
        owner_id = validated_data.pop('owner_id', None)
        
        # Handle location (convert from [lng, lat] to GeoJSON Point)
        if location and len(location) == 2:
            validated_data['location'] = {
                'type': 'Point',
                'coordinates': [float(location[0]), float(location[1])]
            }
        
        # Handle owner
        if owner_id:
            from apps.users.models import User
            try:
                owner = User.objects.get(id=owner_id)
                validated_data['owner'] = owner
            except User.DoesNotExist:
                raise serializers.ValidationError({'owner_id': 'Owner not found'})
        
        court = Court(**validated_data)
        court.save()
        return court
    
    def update(self, instance, validated_data):
        """Update court"""
        location = validated_data.pop('location', None)
        owner_id = validated_data.pop('owner_id', None)
        tariffs_data = validated_data.pop('tariffs', None)
        
        # Handle location
        if location and len(location) == 2:
            instance.location = {
                'type': 'Point',
                'coordinates': [float(location[0]), float(location[1])]
            }
        
        # Handle owner
        if owner_id:
            from apps.users.models import User
            try:
                owner = User.objects.get(id=owner_id)
                instance.owner = owner
            except User.DoesNotExist:
                raise serializers.ValidationError({'owner_id': 'Owner not found'})
        elif 'owner_id' in validated_data:
            instance.owner = None
        
        # Handle tariffs - convert dicts to Tariff instances
        if tariffs_data is not None:
            from apps.courts.models import Tariff
            tariff_instances = []
            for tariff_data in tariffs_data:
                if isinstance(tariff_data, dict):
                    tariff_instances.append(Tariff(**tariff_data))
                else:
                    tariff_instances.append(tariff_data)
            instance.tariffs = tariff_instances
        
        # Update other fields
        for key, value in validated_data.items():
            setattr(instance, key, value)
        
        instance.save()
        return instance


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
        return getattr(obj, '_distance', None)
    
    def to_representation(self, instance):
        """Convert relative image URLs to absolute"""
        ret = super().to_representation(instance)
        
        # Convert relative image URLs to absolute URLs
        if ret.get('images'):
            request = self.context.get('request')
            absolute_images = []
            for img_url in ret['images']:
                if img_url and not img_url.startswith('http'):
                    if request:
                        absolute_url = request.build_absolute_uri(img_url)
                        absolute_images.append(absolute_url)
                    else:
                        from django.conf import settings
                        base_url = getattr(settings, 'BASE_URL', 'http://192.168.31.106:8000')
                        absolute_images.append(f"{base_url}{img_url}")
                else:
                    absolute_images.append(img_url)
            ret['images'] = absolute_images
        
        return ret


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
    
    def to_representation(self, instance):
        """Convert relative image URLs to absolute"""
        ret = super().to_representation(instance)
        
        # Convert relative image URLs to absolute URLs
        if ret.get('images'):
            request = self.context.get('request')
            absolute_images = []
            for img_url in ret['images']:
                if img_url and not img_url.startswith('http'):
                    if request:
                        absolute_url = request.build_absolute_uri(img_url)
                        absolute_images.append(absolute_url)
                    else:
                        from django.conf import settings
                        base_url = getattr(settings, 'BASE_URL', 'http://192.168.31.106:8000')
                        absolute_images.append(f"{base_url}{img_url}")
                else:
                    absolute_images.append(img_url)
            ret['images'] = absolute_images
        
        return ret
