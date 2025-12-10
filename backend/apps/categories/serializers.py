"""
Category serializers
"""
from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name_i18n', 'description_i18n', 'parent', 'children']
        read_only_fields = ['id']
    
    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data if children.exists() else []

