"""
Admin Category URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.categories.views.admin import AdminCategoryViewSet

router = DefaultRouter()
router.register(r'', AdminCategoryViewSet, basename='admin-category')

urlpatterns = router.urls

