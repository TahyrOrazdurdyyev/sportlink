"""
Category views
"""
from rest_framework import viewsets
from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Category ViewSet (read-only)
    """
    queryset = Category.objects.filter(parent=None)  # Root categories
    serializer_class = CategorySerializer

