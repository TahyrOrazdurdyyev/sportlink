"""
Admin API URLs
"""
from django.urls import path, include

urlpatterns = [
    path('categories/', include('apps.categories.urls.admin')),
    path('courts/', include('apps.courts.urls.admin')),
    path('tariffs/', include('apps.courts.urls.admin_tariffs')),
    path('tournaments/', include('apps.tournaments.urls.admin')),
    path('reports/', include('apps.core.urls.reports')),
]

