"""
Reports/Export URLs
"""
from django.urls import path
from apps.core.views.reports import UserExportView

urlpatterns = [
    path('users/', UserExportView.as_view(), name='export-users'),
]

