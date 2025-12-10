"""
Custom base classes for MongoEngine integration with Django REST Framework
"""
from rest_framework import serializers, viewsets, pagination
from rest_framework.response import Response
from mongoengine import Document, EmbeddedDocument
from mongoengine.errors import ValidationError, DoesNotExist, MultipleObjectsReturned
from django.http import Http404
import uuid


class MongoEngineModelSerializer(serializers.Serializer):
    """Base serializer for MongoEngine documents"""
    
    def __init__(self, *args, **kwargs):
        self.Meta = getattr(self, 'Meta', None)
        if not self.Meta:
            raise ValueError("MongoEngineModelSerializer requires Meta class")
        
        self.Meta.model = getattr(self.Meta, 'model', None)
        if not self.Meta.model:
            raise ValueError("Meta class must specify model")
            
        super().__init__(*args, **kwargs)
    
    def to_internal_value(self, data):
        """Convert input data to internal representation"""
        return data
    
    def to_representation(self, instance):
        """Convert document instance to dict representation"""
        if not instance:
            return {}
        
        ret = {}
        fields = getattr(self.Meta, 'fields', '__all__')
        exclude = getattr(self.Meta, 'exclude', [])
        
        if fields == '__all__':
            fields = [field_name for field_name in instance._fields.keys()]
        
        for field_name in fields:
            if field_name in exclude:
                continue
                
            try:
                field_value = getattr(instance, field_name)
                ret[field_name] = self._serialize_field_value(field_value)
            except AttributeError:
                continue
        
        return ret
    
    def _serialize_field_value(self, value):
        """Serialize individual field values"""
        if value is None:
            return None
        
        # Handle UUID fields
        if isinstance(value, uuid.UUID):
            return str(value)
        
        # Handle embedded documents
        if isinstance(value, EmbeddedDocument):
            return self._serialize_embedded_document(value)
        
        # Handle lists
        if isinstance(value, list):
            return [self._serialize_field_value(item) for item in value]
        
        # Handle reference fields
        if isinstance(value, Document):
            return str(value.id) if hasattr(value, 'id') else str(value.pk)
        
        # Handle datetime
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        
        # Handle decimal
        if hasattr(value, '__float__'):
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
        
        # Default: return as-is
        return value
    
    def _serialize_embedded_document(self, doc):
        """Serialize embedded document"""
        ret = {}
        for field_name, field in doc._fields.items():
            try:
                field_value = getattr(doc, field_name)
                ret[field_name] = self._serialize_field_value(field_value)
            except AttributeError:
                continue
        return ret
    
    def create(self, validated_data):
        """Create new document instance"""
        ModelClass = self.Meta.model
        try:
            instance = ModelClass(**validated_data)
            instance.save()
            return instance
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
    
    def update(self, instance, validated_data):
        """Update existing document instance"""
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance
        except ValidationError as e:
            raise serializers.ValidationError(str(e))


class MongoEngineModelViewSet(viewsets.ModelViewSet):
    """Base viewset for MongoEngine documents"""
    
    def get_queryset(self):
        """Get the queryset for this viewset"""
        if hasattr(self, 'queryset') and self.queryset is not None:
            return self.queryset._clone()
        
        if hasattr(self, 'model'):
            return self.model.objects.all()
        
        raise NotImplementedError("Must define queryset or model")
    
    def get_object(self):
        """Get single object by pk"""
        queryset = self.get_queryset()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        
        try:
            obj = queryset.get(**filter_kwargs)
        except (DoesNotExist, ValidationError):
            raise Http404("No document found matching the query")
        except MultipleObjectsReturned:
            raise Http404("Multiple documents found matching the query")
        
        # Check permissions
        self.check_object_permissions(self.request, obj)
        return obj
    
    def perform_create(self, serializer):
        """Perform the creation of new instance"""
        serializer.save()
    
    def perform_update(self, serializer):
        """Perform the update of existing instance"""
        serializer.save()
    
    def perform_destroy(self, instance):
        """Perform the deletion of instance"""
        instance.delete()


class MongoEnginePagination(pagination.PageNumberPagination):
    """Pagination class for MongoEngine querysets"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def paginate_queryset(self, queryset, request, view=None):
        """Paginate MongoEngine queryset"""
        page_size = self.get_page_size(request)
        if not page_size:
            return None
        
        page_number = request.query_params.get(self.page_query_param, 1)
        try:
            page_number = int(page_number)
        except (TypeError, ValueError):
            page_number = 1
        
        if page_number < 1:
            page_number = 1
        
        # Calculate offset
        offset = (page_number - 1) * page_size
        
        # Get total count
        self.count = queryset.count()
        
        # Apply pagination
        self.queryset = queryset.skip(offset).limit(page_size)
        
        # Calculate pagination info
        self.page_number = page_number
        self.page_size = page_size
        
        return list(self.queryset)
    
    def get_paginated_response(self, data):
        """Return paginated response"""
        return Response({
            'count': self.count,
            'page': self.page_number,
            'page_size': self.page_size,
            'pages': (self.count + self.page_size - 1) // self.page_size,
            'results': data
        })


class GeoQueryMixin:
    """Mixin for geo-spatial queries with MongoDB"""
    
    def filter_by_location(self, queryset, lat, lng, radius_km=10):
        """Filter queryset by location within radius"""
        if not lat or not lng:
            return queryset
        
        # Convert km to meters
        radius_meters = radius_km * 1000
        
        # MongoDB geo query
        return queryset.filter(
            location__near=[float(lng), float(lat)],
            location__max_distance=radius_meters
        )
    
    def annotate_distance(self, queryset, lat, lng):
        """Add distance field to queryset results (manual calculation)"""
        if not lat or not lng:
            return queryset
        
        # Note: MongoDB doesn't support distance annotation like PostGIS
        # We'll calculate distance in the serializer or view
        return queryset
    
    def calculate_distance(self, point1, point2):
        """Calculate distance between two points in km"""
        from math import radians, cos, sin, asin, sqrt
        
        if not point1 or not point2:
            return None
        
        # Convert coordinates to radians
        lat1, lng1 = radians(point1['coordinates'][1]), radians(point1['coordinates'][0])
        lat2, lng2 = radians(point2[1]), radians(point2[0])
        
        # Haversine formula
        dlng = lng2 - lng1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        
        # Earth radius in km
        r = 6371
        
        return c * r
