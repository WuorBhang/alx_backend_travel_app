from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, BookingHistoryViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'booking-history', BookingHistoryViewSet, basename='booking-history')

urlpatterns = [
    path('', include(router.urls)),
]
