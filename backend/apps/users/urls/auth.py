"""
Authentication URLs
"""
from django.urls import path
from apps.users.views.auth import OTPRequestView, OTPVerifyView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('otp/request/', OTPRequestView.as_view(), name='otp-request'),
    path('otp/verify/', OTPVerifyView.as_view(), name='otp-verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]

