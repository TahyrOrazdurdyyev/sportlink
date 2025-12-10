"""
Search URLs
"""
from django.urls import path
from apps.users.views.search import SearchPartnersView

urlpatterns = [
    path('partners/', SearchPartnersView.as_view(), name='search-partners'),
]

