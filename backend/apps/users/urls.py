"""
MongoDB User URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, views_refresh

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    # Auth endpoints
    path('auth/otp/request/', views.otp_request, name='otp-request'),
    path('auth/otp/verify/', views.otp_verify, name='otp-verify'),
    path('auth/token/refresh/', views_refresh.refresh_token, name='token-refresh'),
    path('auth/login/', views.otp_verify, name='admin-login'),  # Alias for admin
    
    # User profile
    path('users/me/', views.user_profile, name='user-profile'),
    path('users/me/update/', views.update_profile, name='update-profile'),
    
    # Partner search
    path('search/partners/', views.SearchPartnersView.as_view(), name='search-partners'),
    
    # Router URLs
    path('', include(router.urls)),
]


