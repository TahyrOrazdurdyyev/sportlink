"""
Match serializers
"""
from rest_framework import serializers
from .models import MatchResult


class MatchResultSerializer(serializers.ModelSerializer):
    """Match result serializer"""
    
    class Meta:
        model = MatchResult
        fields = ['id', 'booking', 'score_data', 'recorded_by', 'created_at']
        read_only_fields = ['id', 'created_at']

