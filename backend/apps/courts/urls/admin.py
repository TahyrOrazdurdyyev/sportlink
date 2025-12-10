"""
Admin Court URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.courts.views.admin import AdminCourtViewSet

router = DefaultRouter()
router.register(r'', AdminCourtViewSet, basename='admin-court')

urlpatterns = router.urls

