"""
Search and matching views
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q, F, FloatField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from .serializers import UserPublicSerializer
from apps.categories.models import Category
import math

User = get_user_model()


class SearchPartnersView(APIView):
    """
    Search for partners with matching algorithm
    GET /search/partners/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get query parameters
        lat = request.query_params.get('lat', type=float)
        lng = request.query_params.get('lng', type=float)
        radius_km = request.query_params.get('radius_km', type=float, default=10.0)
        sport = request.query_params.get('sport')  # category ID
        level_min = request.query_params.get('level_min', type=int)
        level_max = request.query_params.get('level_max', type=int)
        goal = request.query_params.get('goal')
        
        # Use current user's location if not provided
        if not lat or not lng:
            if request.user.location:
                point = request.user.location
                lat, lng = point.y, point.x
            else:
                return Response(
                    {'error': 'Location (lat, lng) is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        user_location = Point(lng, lat, srid=4326)
        
        # Base queryset - exclude current user and inactive/banned users
        queryset = User.objects.filter(
            is_active=True,
            is_banned=False
        ).exclude(id=request.user.id)
        
        # Filter by category/sport
        if sport:
            queryset = queryset.filter(user_categories__category_id=sport).distinct()
        
        # Filter by experience level
        if level_min:
            queryset = queryset.filter(experience_level__gte=level_min)
        if level_max:
            queryset = queryset.filter(experience_level__lte=level_max)
        
        # Filter by goal
        if goal:
            queryset = queryset.filter(goals__contains=[goal])
        
        # Filter by distance (using PostGIS)
        if request.user.location:
            queryset = queryset.filter(
                location__distance_lte=(user_location, radius_km * 1000)  # Convert km to meters
            ).annotate(
                distance=Distance('location', user_location)
            )
        else:
            # If user has no location, skip distance filtering
            queryset = queryset.annotate(
                distance=Coalesce(F('location__distance'), 0, output_field=FloatField())
            )
        
        # Calculate match scores
        results = []
        from django.conf import settings
        weights = settings.MATCHING_WEIGHTS
        
        current_time = timezone.now()
        
        for user in queryset[:100]:  # Limit to 100 results
            score = 0.0
            
            # Distance score (0-1, closer = higher score)
            if user.location and hasattr(user, 'distance'):
                distance_km = user.distance.km if hasattr(user.distance, 'km') else 999
                distance_score = max(0, 1 - (distance_km / radius_km))
                score += distance_score * weights['distance']
            
            # Level difference score (0-1, smaller difference = higher score)
            if request.user.experience_level and user.experience_level:
                level_diff = abs(request.user.experience_level - user.experience_level)
                max_diff = 6  # 1-7 scale
                level_score = 1 - (level_diff / max_diff)
                score += level_score * weights['level_difference']
            
            # Last active score (0-1, more recent = higher score)
            if user.last_active_at:
                hours_since_active = (current_time - user.last_active_at).total_seconds() / 3600
                days_since_active = hours_since_active / 24
                # Score decreases over 30 days
                active_score = max(0, 1 - (days_since_active / 30))
                score += active_score * weights['last_active']
            else:
                score += 0.1 * weights['last_active']  # Low score for no activity
            
            results.append({
                'user': user,
                'score': score,
                'distance_km': distance_km if user.location and hasattr(user, 'distance') else None
            })
        
        # Sort by score (descending)
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # Serialize results
        serializer_data = []
        for result in results[:50]:  # Return top 50
            user_data = UserPublicSerializer(result['user']).data
            user_data['match_score'] = round(result['score'], 3)
            if result['distance_km']:
                user_data['distance'] = round(result['distance_km'], 2)
            serializer_data.append(user_data)
        
        return Response({
            'count': len(serializer_data),
            'results': serializer_data
        })

