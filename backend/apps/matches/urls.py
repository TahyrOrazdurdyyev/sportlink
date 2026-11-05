"""
Match URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.matches.views import MatchResultViewSet

router = DefaultRouter()
router.register(r'results', MatchResultViewSet, basename='match-result')

urlpatterns = router.urls

