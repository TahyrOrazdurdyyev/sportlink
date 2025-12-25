"""
Notification URLs
"""
from django.urls import path
from apps.notifications import views

urlpatterns = [
    path('notifications/', views.list_notifications, name='list-notifications'),
    path('notifications/<uuid:pk>/mark_read/', views.mark_notification_read, name='mark-notification-read'),
    path('notifications/mark_all_read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    path('notifications/unread_count/', views.unread_count, name='unread-count'),
    path('push-tokens/register/', views.register_token, name='register-push-token'),
    path('push-tokens/unregister/', views.unregister_token, name='unregister-push-token'),
]
