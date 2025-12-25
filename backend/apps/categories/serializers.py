"""
Category serializers for MongoDB
"""
from rest_framework import serializers
from apps.core.mongoengine_drf import MongoEngineModelSerializer
from .models import Category


class CategorySerializer(MongoEngineModelSerializer):
    """Category serializer"""
    id = serializers.UUIDField(read_only=True)
    parent_id = serializers.UUIDField(required=False, allow_null=True)
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name_i18n', 'description_i18n', 'parent_id', 'children_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Override to add children_count"""
        ret = super().to_representation(instance)
        ret['children_count'] = self.get_children_count(instance)
        return ret
    
    def get_children_count(self, obj):
        """Get count of child categories"""
        return Category.objects.filter(parent=obj).count()
    
    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        if parent_id:
            try:
                parent = Category.objects.get(id=parent_id)
                validated_data['parent'] = parent
            except Category.DoesNotExist:
                raise serializers.ValidationError({'parent_id': 'Parent category not found'})
        
        category = Category(**validated_data)
        category.save()
        return category
    
    def update(self, instance, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        if parent_id:
            try:
                parent = Category.objects.get(id=parent_id)
                instance.parent = parent
            except Category.DoesNotExist:
                raise serializers.ValidationError({'parent_id': 'Parent category not found'})
        elif 'parent_id' in validated_data:
            instance.parent = None
        
        for key, value in validated_data.items():
            setattr(instance, key, value)
        
        instance.save()
        return instance

