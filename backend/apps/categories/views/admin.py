"""
Admin category views
"""
from rest_framework import viewsets
from apps.core.permissions import IsAdminUser
from ..models import Category
from ..serializers import CategorySerializer


class AdminCategoryViewSet(viewsets.ModelViewSet):
    """
    Admin Category CRUD
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]

