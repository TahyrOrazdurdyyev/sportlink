"""
MongoDB Booking URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_matching

router = DefaultRouter()
router.register(r'bookings', views.BookingViewSet, basename='booking')

urlpatterns = [
    # Check availability
    path('bookings/check-availability/', views.check_availability, name='check-availability'),
    
    # Weekly booking limits
    path('bookings/weekly-limits/', views.get_weekly_limits, name='weekly-limits'),
    
    # Booking actions
    path('bookings/<uuid:booking_id>/cancel/', views.cancel_booking, name='cancel-booking'),
    path('bookings/<uuid:booking_id>/confirm/', views.confirm_booking, name='confirm-booking'),
    
    # Opponent matching
    path('bookings/<uuid:booking_id>/matches/', views_matching.get_booking_matches, name='booking-matches'),
    path('bookings/matches/my/', views_matching.get_my_matches, name='my-matches'),
    path('bookings/matches/find/', views_matching.find_potential_opponents, name='find-opponents'),
    
    # User bookings
    path('users/bookings/', views.UserBookingsView.as_view(), name='user-bookings'),
    
    # Router URLs
    path('', include(router.urls)),
]
