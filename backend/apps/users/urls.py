"""
MongoDB User URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, views_refresh, views_matching, views_statistics, views_upload

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
# Remove admin users from router - using simple function views instead

urlpatterns = [
    # Auth endpoints
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/token/refresh/', views_refresh.refresh_token, name='token-refresh'),
    
    # User profile
    path('users/me/', views.user_profile, name='user-profile'),
    path('users/me/update/', views.update_profile, name='update-profile'),
    path('users/me/change-password/', views.change_password, name='change-password'),
    path('users/fcm-token/', views.update_fcm_token, name='update-fcm-token'),
    
    # Avatar upload/delete
    path('users/avatar/upload/', views_upload.upload_avatar, name='upload-avatar'),
    path('users/avatar/delete/', views_upload.delete_avatar, name='delete-avatar'),
    
    # Opponent matching
    path('users/find-opponents/', views_matching.find_opponents, name='find-opponents'),
    path('users/match-invitation/', views_matching.send_match_invitation, name='match-invitation'),
    
    # Statistics
    path('users/statistics/', views_statistics.user_statistics, name='user-statistics'),
    path('users/<uuid:user_id>/statistics/', views_statistics.user_statistics, name='user-statistics-detail'),
    path('users/achievements/', views_statistics.user_achievements, name='user-achievements'),
    path('users/leaderboard/', views_statistics.user_leaderboard, name='leaderboard'),
    
    # Partner search
    path('search/partners/', views.SearchPartnersView.as_view(), name='search-partners'),
    
    # Admin endpoints - using simple function views
    path('admin/users/', views.admin_list_users, name='admin-list-users'),
    
    # Router URLs
    path('', include(router.urls)),
]


