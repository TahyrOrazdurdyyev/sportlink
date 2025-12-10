"""
User URLs
"""
from django.urls import path
from apps.users.views.users import UserProfileView, UserPublicView

urlpatterns = [
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('<uuid:user_id>/', UserPublicView.as_view(), name='user-public'),
]

