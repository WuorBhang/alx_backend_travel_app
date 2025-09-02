from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TripViewSet, DestinationViewSet

router = DefaultRouter()
router.register(r'trips', TripViewSet, basename='trip')
router.register(r'destinations', DestinationViewSet, basename='destination')

urlpatterns = [
    path('', include(router.urls)),
]
