"""
Tournament serializers for MongoDB
"""
from rest_framework import serializers
from apps.core.mongoengine_drf import MongoEngineModelSerializer
from apps.tournaments.models import Tournament


class TournamentSerializer(MongoEngineModelSerializer):
    """Full tournament serializer for admin"""
    id = serializers.UUIDField(read_only=True)
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tournament
        fields = [
            'id', 'name_i18n', 'description_i18n', 'image_url',
            'location_description', 'country', 'city', 'organizer_name', 'registration_link',
            'start_date', 'end_date', 'registration_deadline',
            'max_participants', 'min_participants',
            'registration_open', 'registration_fee',
            'status', 'participant_count', 'categories', 'rules', 'prizes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Override to add participant_count and fix booleans"""
        ret = super().to_representation(instance)
        ret['participant_count'] = self.get_participant_count(instance)
        # Ensure booleans are actual booleans, not numbers
        ret['registration_open'] = bool(instance.registration_open)
        
        # Convert relative image URL to absolute URL
        if ret.get('image_url') and not ret['image_url'].startswith('http'):
            request = self.context.get('request')
            if request:
                ret['image_url'] = request.build_absolute_uri(ret['image_url'])
            else:
                # Fallback if no request in context
                from django.conf import settings
                base_url = getattr(settings, 'BASE_URL', 'http://192.168.31.106:8000')
                ret['image_url'] = f"{base_url}{ret['image_url']}"
        
        return ret
    
    def get_participant_count(self, obj):
        """Get count of accepted participants"""
        return obj.get_participant_count()


class TournamentParticipantSerializer(serializers.Serializer):
    """Tournament participant serializer"""
    user = serializers.StringRelatedField(read_only=True)
    status = serializers.CharField(read_only=True)
    registration_date = serializers.DateTimeField(read_only=True)

