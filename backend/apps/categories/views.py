"""
Category views for MongoDB
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.core.mongoengine_drf import MongoEngineModelViewSet
from apps.core.permissions import IsAdminUser
from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(MongoEngineModelViewSet):
    """
    Category ViewSet with full CRUD
    """
    serializer_class = CategorySerializer
    
    def get_permissions(self):
        """Allow read for all, write only for admin"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]
    
    def get_queryset(self):
        """Get all categories or filter by parent"""
        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            try:
                parent = Category.objects.get(id=parent_id)
                return Category.objects.filter(parent=parent)
            except Category.DoesNotExist:
                return Category.objects.none()
        
        # Return root categories by default
        return Category.objects.filter(parent=None)
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """Get all children of a category"""
        category = self.get_object()
        children = Category.objects.filter(parent=category)
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data)

