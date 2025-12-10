"""
Tournament serializers
"""
from rest_framework import serializers
from .models import Tournament, TournamentParticipant
from apps.courts.serializers import CourtSerializer


class TournamentSerializer(serializers.ModelSerializer):
    """Tournament serializer"""
    courts = CourtSerializer(many=True, read_only=True)
    court_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    participant_count = serializers.SerializerMethodField()
    is_registered = serializers.SerializerMethodField()
    
    class Meta:
        model = Tournament
        fields = [
            'id', 'name_i18n', 'description_i18n', 'courts', 'court_ids',
            'organizer_info', 'start_date', 'end_date',
            'max_participants', 'registration_open', 'registration_link',
            'participant_count', 'is_registered', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_participant_count(self, obj):
        return obj.participants.filter(status__in=['accepted', 'paid']).count()
    
    def get_is_registered(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participants.filter(
                user=request.user,
                status__in=['applied', 'accepted', 'paid']
            ).exists()
        return False


class TournamentParticipantSerializer(serializers.ModelSerializer):
    """Tournament participant serializer"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = TournamentParticipant
        fields = ['id', 'user', 'status', 'applied_at', 'updated_at']
        read_only_fields = ['id', 'applied_at', 'updated_at']

