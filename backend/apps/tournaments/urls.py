"""
Tournament URLs for MongoDB
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tournaments.views import TournamentViewSet, AdminTournamentViewSet
from apps.tournaments import views_upload, views_registration, views_participants

router = DefaultRouter()
router.register(r'tournaments', TournamentViewSet, basename='tournament')
router.register(r'admin/tournaments', AdminTournamentViewSet, basename='admin-tournament')

urlpatterns = [
    # Image upload/delete
    path('admin/tournaments/<uuid:tournament_id>/upload-image/', views_upload.upload_tournament_image, name='upload-tournament-image'),
    path('admin/tournaments/<uuid:tournament_id>/delete-image/', views_upload.delete_tournament_image, name='delete-tournament-image'),
    
    # Tournament registration (user endpoints)
    path('tournaments/<uuid:tournament_id>/register/', views_registration.register_for_tournament, name='register-tournament'),
    path('tournaments/<uuid:tournament_id>/cancel-registration/', views_registration.cancel_tournament_registration, name='cancel-tournament-registration'),
    path('tournaments/my-registrations/', views_registration.get_my_tournament_registrations, name='my-tournament-registrations'),
    
    # Tournament participants (admin endpoints)
    path('admin/tournaments/<uuid:tournament_id>/participants/', views_participants.get_tournament_participants, name='tournament-participants'),
    
    # Router URLs
    path('', include(router.urls)),
]

