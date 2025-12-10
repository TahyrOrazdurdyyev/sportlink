"""
Admin Tournament URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tournaments.views.admin import AdminTournamentViewSet

router = DefaultRouter()
router.register(r'', AdminTournamentViewSet, basename='admin-tournament')

urlpatterns = router.urls

