"""
MongoDB Court URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'courts', views.CourtViewSet, basename='court')
router.register(r'admin/courts', views.AdminCourtViewSet, basename='admin-court')

urlpatterns = [
    # Court availability
    path('courts/<uuid:court_id>/availability/', views.court_availability, name='court-availability'),
    
    # Router URLs
    path('', include(router.urls)),
]
