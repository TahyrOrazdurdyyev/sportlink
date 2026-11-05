"""
MongoDB Court URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, views_upload

router = DefaultRouter()
router.register(r'courts', views.CourtViewSet, basename='court')
router.register(r'admin/courts', views.AdminCourtViewSet, basename='admin-court')

urlpatterns = [
    # Court availability
    path('courts/<uuid:court_id>/availability/', views.court_availability, name='court-availability'),
    
    # Image upload/delete
    path('admin/courts/upload-image/', views_upload.upload_court_image, name='upload-court-image'),
    path('admin/courts/<uuid:court_id>/images/<int:image_index>/', views_upload.delete_court_image, name='delete-court-image'),
    
    # Router URLs
    path('', include(router.urls)),
]
