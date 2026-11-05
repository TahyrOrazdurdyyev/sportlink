"""
Legal documents serializers
"""
from rest_framework import serializers
from apps.core.models_legal import LegalDocument


class LegalDocumentSerializer(serializers.Serializer):
    """Serializer for Legal Documents"""
    id = serializers.CharField(read_only=True)
    document_type = serializers.CharField()
    title = serializers.DictField()
    content = serializers.DictField()
    version = serializers.CharField()
    effective_date = serializers.DateTimeField()
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return LegalDocument.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

