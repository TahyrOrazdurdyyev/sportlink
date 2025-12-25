"""
Tournament URLs for MongoDB
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tournaments.views import TournamentViewSet, AdminTournamentViewSet
from apps.tournaments import views_upload

router = DefaultRouter()
router.register(r'tournaments', TournamentViewSet, basename='tournament')
router.register(r'admin/tournaments', AdminTournamentViewSet, basename='admin-tournament')

urlpatterns = [
    # Image upload/delete
    path('admin/tournaments/<uuid:tournament_id>/upload-image/', views_upload.upload_tournament_image, name='upload-tournament-image'),
    path('admin/tournaments/<uuid:tournament_id>/delete-image/', views_upload.delete_tournament_image, name='delete-tournament-image'),
    
    # Router URLs
    path('', include(router.urls)),
]

