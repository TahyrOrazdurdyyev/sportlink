"""
Admin Tariff URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.courts.views.admin import AdminTariffViewSet

router = DefaultRouter()
router.register(r'', AdminTariffViewSet, basename='admin-tariff')

urlpatterns = router.urls

