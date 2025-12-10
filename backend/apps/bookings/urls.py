"""
MongoDB Booking URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'bookings', views.BookingViewSet, basename='booking')

urlpatterns = [
    # Booking actions
    path('bookings/<uuid:booking_id>/cancel/', views.cancel_booking, name='cancel-booking'),
    path('bookings/<uuid:booking_id>/confirm/', views.confirm_booking, name='confirm-booking'),
    
    # User bookings
    path('users/bookings/', views.UserBookingsView.as_view(), name='user-bookings'),
    
    # Router URLs
    path('', include(router.urls)),
]
