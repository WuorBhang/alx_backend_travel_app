from rest_framework import serializers
from .models import Booking, BookingHistory
from trips.serializers import TripListSerializer


class BookingHistorySerializer(serializers.ModelSerializer):
    """Serializer for booking history"""
    
    class Meta:
        model = BookingHistory
        fields = [
            'id', 'old_status', 'new_status', 'changed_by', 
            'change_reason', 'changed_at'
        ]
        read_only_fields = ['id', 'changed_at']


class BookingListSerializer(serializers.ModelSerializer):
    """Serializer for listing bookings"""
    trip = TripListSerializer(read_only=True)
    can_cancel = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'trip', 'number_of_people', 'total_price', 'status',
            'booking_date', 'can_cancel', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'total_price', 'booking_date', 'created_at']


class BookingDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed booking view"""
    trip = TripListSerializer(read_only=True)
    history = BookingHistorySerializer(many=True, read_only=True)
    can_cancel = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'trip', 'number_of_people', 'total_price', 'status',
            'booking_date', 'confirmation_date', 'cancellation_date',
            'special_requests', 'contact_phone', 'contact_email',
            'can_cancel', 'is_active', 'history', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_price', 'booking_date', 'confirmation_date',
            'cancellation_date', 'can_cancel', 'is_active', 'history',
            'created_at', 'updated_at'
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new bookings"""
    
    class Meta:
        model = Booking
        fields = [
            'trip', 'number_of_people', 'special_requests',
            'contact_phone', 'contact_email'
        ]
    
    def validate(self, data):
        """Validate booking data"""
        trip = data.get('trip')
        number_of_people = data.get('number_of_people')
        
        if trip and number_of_people:
            # Check if trip can be booked
            if not trip.can_book():
                raise serializers.ValidationError(
                    "This trip cannot be booked at the moment"
                )
            
            # Check if there are enough spots
            if trip.available_spots < number_of_people:
                raise serializers.ValidationError(
                    f"Only {trip.available_spots} spots available for this trip"
                )
            
            # Check if user already has a booking for this trip
            user = self.context['request'].user
            if Booking.objects.filter(
                user=user, 
                trip=trip, 
                status__in=['pending', 'confirmed']
            ).exists():
                raise serializers.ValidationError(
                    "You already have a booking for this trip"
                )
        
        return data

    def create(self, validated_data):
        """Create booking with calculated total price"""
        trip = validated_data['trip']
        number_of_people = validated_data['number_of_people']
        
        # Calculate total price
        total_price = trip.price * number_of_people
        
        # Create booking
        booking = Booking.objects.create(
            user=self.context['request'].user,
            total_price=total_price,
            **validated_data
        )
        
        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating bookings"""
    
    class Meta:
        model = Booking
        fields = [
            'number_of_people', 'special_requests', 'contact_phone', 'contact_email'
        ]
    
    def validate(self, data):
        """Validate update data"""
        if 'number_of_people' in data:
            trip = self.instance.trip
            new_number = data['number_of_people']
            current_number = self.instance.number_of_people
            
            # Calculate additional spots needed
            additional_needed = new_number - current_number
            
            if additional_needed > 0 and trip.available_spots < additional_needed:
                raise serializers.ValidationError(
                    f"Not enough spots available. Only {trip.available_spots} spots left."
                )
        
        return data


class BookingStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating booking status (admin only)"""
    
    class Meta:
        model = Booking
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status change"""
        old_status = self.instance.status
        
        # Prevent invalid status transitions
        if old_status == 'completed' and value != 'completed':
            raise serializers.ValidationError(
                "Cannot change status of completed booking"
            )
        
        if old_status == 'cancelled' and value not in ['cancelled', 'confirmed']:
            raise serializers.ValidationError(
                "Cancelled booking can only be confirmed or remain cancelled"
            )
        
        return value
