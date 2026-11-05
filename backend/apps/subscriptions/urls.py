"""
Subscription Plan URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, views_user, views_request, views_admin

router = DefaultRouter()
router.register(r'plans', views.AdminSubscriptionPlanViewSet, basename='subscription-plan')

urlpatterns = [
    # Admin
    path('features/', views.get_available_features, name='available-features'),
    path('plans/public/', views.get_public_plans, name='public-plans'),
    
    # User subscriptions
    path('my-subscription/', views_user.my_subscription, name='my-subscription'),
    path('subscribe/', views_user.subscribe, name='subscribe'),
    path('cancel/', views_user.cancel_subscription, name='cancel-subscription'),
    path('my-features/', views_user.my_features, name='my-features'),
    
    # Subscription requests
    path('requests/create/', views_request.create_subscription_request, name='create-subscription-request'),
    path('requests/my/', views_request.get_user_subscription_requests, name='my-subscription-requests'),
    path('requests/pending/', views_request.get_pending_subscription_requests, name='pending-subscription-requests'),
    path('requests/all/', views_request.get_all_subscription_requests, name='all-subscription-requests'),
    path('requests/<uuid:request_id>/approve/', views_request.approve_subscription_request, name='approve-subscription-request'),
    path('requests/<uuid:request_id>/reject/', views_request.reject_subscription_request, name='reject-subscription-request'),
    path('requests/<uuid:request_id>/cancel/', views_request.cancel_subscription_request, name='cancel-subscription-request'),
    
    # Admin subscription management
    path('admin/create-manual/', views_admin.create_manual_subscription, name='create-manual-subscription'),
    path('admin/user/<uuid:user_id>/', views_admin.get_user_subscription, name='get-user-subscription'),
    path('admin/user/<uuid:user_id>/cancel/', views_admin.cancel_user_subscription, name='cancel-user-subscription'),
    
    path('', include(router.urls)),
]

