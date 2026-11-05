"""
URL configuration for sportlink project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.users import views_admin
from apps.core.views import statistics
from apps.core import views_legal

urlpatterns = [
    path('admin/', admin.site.urls),
    # Admin API
    path('api/v1/admin/login', views_admin.admin_login, name='admin-login'),
    # Reports & Statistics
    path('api/v1/reports/dashboard/', statistics.dashboard_stats, name='dashboard-stats'),
    path('api/v1/reports/user-growth/', statistics.user_growth_chart, name='user-growth'),
    path('api/v1/reports/booking-stats/', statistics.booking_stats_chart, name='booking-stats'),
    path('api/v1/reports/popular-courts/', statistics.popular_courts, name='popular-courts'),
    # Notifications
    path('api/v1/admin/notifications/', include('apps.notifications.urls')),
    # Subscriptions (both admin and user endpoints)
    path('api/v1/admin/subscriptions/', include('apps.subscriptions.urls')),
    path('api/v1/subscriptions/', include('apps.subscriptions.urls')),
    # Legal documents
    path('api/v1/legal/privacy-policy/', views_legal.get_privacy_policy, name='privacy-policy'),
    path('api/v1/legal/terms-of-service/', views_legal.get_terms_of_service, name='terms-of-service'),
    path('api/v1/admin/legal/', views_legal.manage_legal_documents, name='admin-legal-documents'),
    path('api/v1/admin/legal/<uuid:document_id>/', views_legal.manage_legal_document_detail, name='admin-legal-document-detail'),
    # MongoDB API endpoints
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/categories/', include('apps.categories.urls')),
    path('api/v1/', include('apps.courts.urls')),
    path('api/v1/', include('apps.bookings.urls')),
    path('api/v1/', include('apps.tournaments.urls')),
    path('api/v1/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

