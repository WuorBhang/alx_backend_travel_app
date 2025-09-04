from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Trip, Destination
from .serializers import (
    TripListSerializer, TripDetailSerializer, TripCreateSerializer,
    TripUpdateSerializer, DestinationSerializer
)

class DestinationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for destinations (read-only)
    
    Provides read-only access to travel destinations.
    Users can search and filter destinations by name, country, and description.
    """
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country', 'description']
    ordering_fields = ['name', 'country', 'created_at']
    ordering = ['name']

class TripViewSet(viewsets.ModelViewSet):
    """
    ViewSet for trips with different permissions for different actions
    
    Provides CRUD operations for trips:
    - Regular users can view trips
    - Admin users can create, update, and delete trips
    
    Supports filtering by trip type, destination, featured status, price range,
    date range, duration, and availability.
    """
    queryset = Trip.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['trip_type', 'destination', 'is_featured']
    search_fields = ['title', 'description', 'destination__name', 'destination__country']
    ordering_fields = ['price', 'start_date', 'duration_days', 'created_at']
    ordering = ['start_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        min_duration = self.request.query_params.get('min_duration')
        max_duration = self.request.query_params.get('max_duration')
        if min_duration:
            queryset = queryset.filter(duration_days__gte=min_duration)
        if max_duration:
            queryset = queryset.filter(duration_days__lte=max_duration)
        available_only = self.request.query_params.get('available_only', 'false').lower() == 'true'
        if available_only:
            queryset = queryset.filter(current_bookings__lt=F('max_capacity'))
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return TripCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TripUpdateSerializer
        elif self.action == 'retrieve':
            return TripDetailSerializer
        return TripListSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        method='get',
        operation_description="Get all featured trips",
        responses={200: TripListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], serializer_class=TripListSerializer)
    def featured(self, request):
        """Get featured trips"""
        featured_trips = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured_trips, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_description="Get upcoming trips (starting in the future), limited to 10 results",
        responses={200: TripListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], serializer_class=TripListSerializer)
    def upcoming(self, request):
        """Get upcoming trips (starting in the future)"""
        upcoming_trips = self.get_queryset().filter(
            start_date__gt=timezone.now().date()
        ).order_by('start_date')[:10]
        serializer = self.get_serializer(upcoming_trips, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_description="Advanced search for trips by title, description, destination name, or country",
        manual_parameters=[
            openapi.Parameter('q', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING, required=True)
        ],
        responses={
            200: openapi.Response('Search Results', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'query': openapi.Schema(type=openapi.TYPE_STRING),
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'results': TripListSerializer(many=True)
                }
            )),
            400: openapi.Response('Bad Request', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
            ))
        }
    )
    @action(detail=False, methods=['get'], serializer_class=TripListSerializer)
    def search(self, request):
        """Advanced search for trips"""
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {'error': 'Search query parameter "q" is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
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

    @swagger_auto_schema(
        method='get',
        operation_description="Get detailed availability information for a specific trip",
        responses={
            200: openapi.Response('Availability Info', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'trip_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'title': openapi.Schema(type=openapi.TYPE_STRING),
                    'max_capacity': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'current_bookings': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'available_spots': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'is_fully_booked': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'can_book': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'booking_percentage': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'start_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                    'end_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                    'is_past': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                }
            ))
        }
    )
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
            'booking_percentage': (trip.current_bookings / trip.max_capacity) * 100 if trip.max_capacity > 0 else 0,
            'start_date': trip.start_date,
            'end_date': trip.end_date,
            'is_past': trip.is_past
        })

    @swagger_auto_schema(
        method='get',
        operation_description="Get trips filtered by destination ID",
        manual_parameters=[
            openapi.Parameter('destination_id', openapi.IN_QUERY, description="Destination ID", type=openapi.TYPE_INTEGER, required=True)
        ],
        responses={
            200: openapi.Response('Trips by Destination', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'destination_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'trips': TripListSerializer(many=True)
                }
            )),
            400: openapi.Response('Bad Request', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
            ))
        }
    )
    @action(detail=False, methods=['get'], serializer_class=TripListSerializer)
    def by_destination(self, request):
        """Get trips filtered by destination"""
        destination_id = request.query_params.get('destination_id')
        if not destination_id:
            return Response(
                {'error': 'destination_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            destination_trips = self.get_queryset().filter(destination_id=destination_id)
            serializer = self.get_serializer(destination_trips, many=True)
            return Response({
                'destination_id': destination_id,
                'count': destination_trips.count(),
                'trips': serializer.data
            })
        except Exception as e:
            return Response(
                {'error': 'Invalid destination_id'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        method='get',
        operation_description="Get trips filtered by trip type",
        manual_parameters=[
            openapi.Parameter('type', openapi.IN_QUERY, description="Trip type (adventure, cultural, relaxation, business, family, romantic)", type=openapi.TYPE_STRING, required=True)
        ],
        responses={
            200: openapi.Response('Trips by Type', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'trip_type': openapi.Schema(type=openapi.TYPE_STRING),
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'trips': TripListSerializer(many=True)
                }
            )),
            400: openapi.Response('Bad Request', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
            ))
        }
    )
    @action(detail=False, methods=['get'], serializer_class=TripListSerializer)
    def by_type(self, request):
        """Get trips filtered by trip type"""
        trip_type = request.query_params.get('type')
        if not trip_type:
            return Response(
                {'error': 'type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate trip type
        valid_types = [choice[0] for choice in Trip.TRIP_TYPES]
        if trip_type not in valid_types:
            return Response(
                {
                    'error': f'Invalid trip type. Valid types are: {", ".join(valid_types)}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        type_trips = self.get_queryset().filter(trip_type=trip_type)
        serializer = self.get_serializer(type_trips, many=True)
        return Response({
            'trip_type': trip_type,
            'count': type_trips.count(),
            'trips': serializer.data
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get trip statistics (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset()
        total_trips = queryset.count()
        active_trips = queryset.filter(is_active=True).count()
        featured_trips = queryset.filter(is_featured=True).count()
        fully_booked = queryset.filter(current_bookings__gte=F('max_capacity')).count()
        
        # Trip type distribution
        trip_types = {}
        for trip_type, display_name in Trip.TRIP_TYPES:
            count = queryset.filter(trip_type=trip_type).count()
            trip_types[trip_type] = {
                'name': display_name,
                'count': count
            }
        
        # Booking statistics
        total_capacity = sum(trip.max_capacity for trip in queryset)
        total_bookings = sum(trip.current_bookings for trip in queryset)
        
        return Response({
            'total_trips': total_trips,
            'active_trips': active_trips,
            'featured_trips': featured_trips,
            'fully_booked_trips': fully_booked,
            'trip_types': trip_types,
            'booking_stats': {
                'total_capacity': total_capacity,
                'total_bookings': total_bookings,
                'overall_booking_rate': (total_bookings / total_capacity * 100) if total_capacity > 0 else 0
            }
        })

    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        """Toggle featured status of a trip (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        trip = self.get_object()
        trip.is_featured = not trip.is_featured
        trip.save()
        
        return Response({
            'trip_id': trip.id,
            'title': trip.title,
            'is_featured': trip.is_featured,
            'message': f'Trip {"featured" if trip.is_featured else "unfeatured"} successfully'
        })

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle active status of a trip (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        trip = self.get_object()
        trip.is_active = not trip.is_active
        trip.save()
        
        return Response({
            'trip_id': trip.id,
            'title': trip.title,
            'is_active': trip.is_active,
            'message': f'Trip {"activated" if trip.is_active else "deactivated"} successfully'
        })

    def perform_create(self, serializer):
        """Override to add any additional logic when creating trips"""
        serializer.save()

    def perform_update(self, serializer):
        """Override to add any additional logic when updating trips"""
        serializer.save()

    def perform_destroy(self, serializer):
        """Override to soft delete instead of hard delete"""
        serializer.is_active = False
        serializer.save()