from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

from .models import Trip, Destination
from .serializers import (
    TripListSerializer, TripDetailSerializer, TripCreateSerializer,
    TripUpdateSerializer, DestinationSerializer
)


class DestinationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for destinations (read-only)"""
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country', 'description']
    ordering_fields = ['name', 'country', 'created_at']
    ordering = ['name']


class TripViewSet(viewsets.ModelViewSet):
    """ViewSet for trips with different permissions for different actions"""
    queryset = Trip.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['trip_type', 'destination', 'is_featured']
    search_fields = ['title', 'description', 'destination__name', 'destination__country']
    ordering_fields = ['price', 'start_date', 'duration_days', 'created_at']
    ordering = ['start_date']

    def get_queryset(self):
        """Filter queryset based on user permissions and request"""
        queryset = super().get_queryset()
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        # Filter by price range if provided
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filter by duration if provided
        min_duration = self.request.query_params.get('min_duration')
        max_duration = self.request.query_params.get('max_duration')
        
        if min_duration:
            queryset = queryset.filter(duration_days__gte=min_duration)
        if max_duration:
            queryset = queryset.filter(duration_days__lte=max_duration)
        
        # Filter by availability
        available_only = self.request.query_params.get('available_only', 'false').lower() == 'true'
        if available_only:
            from django.db.models import F
            queryset = queryset.filter(current_bookings__lt=F('max_capacity'))
        
        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return TripCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TripUpdateSerializer
        elif self.action == 'retrieve':
            return TripDetailSerializer
        return TripListSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured trips"""
        featured_trips = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured_trips, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming trips (starting in the future)"""
        upcoming_trips = self.get_queryset().filter(
            start_date__gt=timezone.now().date()
        ).order_by('start_date')[:10]
        serializer = self.get_serializer(upcoming_trips, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search for trips"""
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {'error': 'Search query parameter "q" is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Search in title, description, destination name and country
        search_results = self.get_queryset().filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(destination__name__icontains=query) |
            Q(destination__country__icontains=query)
        )
        
        serializer = self.get_serializer(search_results, many=True)
        return Response({
            'query': query,
            'count': search_results.count(),
            'results': serializer.data
        })

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Get detailed availability information for a trip"""
        trip = self.get_object()
        return Response({
            'trip_id': trip.id,
            'title': trip.title,
            'max_capacity': trip.max_capacity,
            'current_bookings': trip.current_bookings,
            'available_spots': trip.available_spots,
            'is_fully_booked': trip.is_fully_booked,
            'can_book': trip.can_book(),
            'booking_percentage': (trip.current_bookings / trip.max_capacity) * 100
        })
