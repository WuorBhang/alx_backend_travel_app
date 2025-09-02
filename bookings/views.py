from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone

from .models import Booking, BookingHistory
from .serializers import (
    BookingListSerializer, BookingDetailSerializer, BookingCreateSerializer,
    BookingUpdateSerializer, BookingStatusUpdateSerializer, BookingHistorySerializer
)


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing bookings"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'trip', 'trip__trip_type']
    search_fields = ['trip__title', 'trip__destination__name']
    ordering_fields = ['booking_date', 'total_price', 'created_at']
    ordering = ['-booking_date']

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        
        if user.is_staff:
            # Staff can see all bookings
            return Booking.objects.all().select_related('trip', 'trip__destination', 'user')
        else:
            # Regular users can only see their own bookings
            return Booking.objects.filter(user=user).select_related('trip', 'trip__destination')

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BookingUpdateSerializer
        elif self.action == 'retrieve':
            return BookingDetailSerializer
        elif self.action == 'update_status':
            return BookingStatusUpdateSerializer
        return BookingListSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action in ['update_status', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()
        
        if not booking.can_cancel:
            return Response(
                {'error': 'This booking cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if booking.cancel_booking():
            return Response(
                {'message': 'Booking cancelled successfully'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Failed to cancel booking'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a booking"""
        booking = self.get_object()
        
        if booking.confirm_booking():
            return Response(
                {'message': 'Booking confirmed successfully'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Failed to confirm booking'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """Get current user's bookings"""
        user_bookings = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(user_bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active bookings (pending or confirmed)"""
        active_bookings = self.get_queryset().filter(
            status__in=['pending', 'confirmed']
        )
        serializer = self.get_serializer(active_bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming bookings"""
        upcoming_bookings = self.get_queryset().filter(
            status__in=['pending', 'confirmed'],
            trip__start_date__gt=timezone.now().date()
        ).order_by('trip__start_date')
        serializer = self.get_serializer(upcoming_bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self, request):
        """Get past bookings"""
        past_bookings = self.get_queryset().filter(
            trip__end_date__lt=timezone.now().date()
        ).order_by('-trip__end_date')
        serializer = self.get_serializer(past_bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update booking status (admin only)"""
        booking = self.get_object()
        serializer = self.get_serializer(booking, data=request.data, partial=True)
        
        if serializer.is_valid():
            old_status = booking.status
            serializer.save()
            
            # Log the status change
            BookingHistory.objects.create(
                booking=booking,
                old_status=old_status,
                new_status=booking.status,
                changed_by=request.user,
                change_reason=request.data.get('change_reason', '')
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get booking history"""
        booking = self.get_object()
        history = booking.history.all()
        serializer = BookingHistorySerializer(history, many=True)
        return Response(serializer.data)


class BookingHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for booking history (admin only)"""
    queryset = BookingHistory.objects.all().select_related('booking', 'changed_by')
    serializer_class = BookingHistorySerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['new_status', 'changed_by']
    ordering_fields = ['changed_at']
    ordering = ['-changed_at']
