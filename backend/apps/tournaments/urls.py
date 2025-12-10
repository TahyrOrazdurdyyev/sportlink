"""
Tournament URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tournaments.views import TournamentViewSet

router = DefaultRouter()
router.register(r'', TournamentViewSet, basename='tournament')

urlpatterns = router.urls

