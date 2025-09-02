from rest_framework import serializers
from .models import Trip, Destination
from django.utils import timezone


class DestinationSerializer(serializers.ModelSerializer):
    """Serializer for Destination model"""
    
    class Meta:
        model = Destination
        fields = [
            'id', 'name', 'country', 'description', 
            'image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TripListSerializer(serializers.ModelSerializer):
    """Serializer for listing trips (public view)"""
    destination = DestinationSerializer(read_only=True)
    available_spots = serializers.ReadOnlyField()
    is_fully_booked = serializers.ReadOnlyField()
    can_book = serializers.ReadOnlyField()
    
    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'destination', 'trip_type', 'duration_days',
            'price', 'max_capacity', 'current_bookings', 'available_spots',
            'start_date', 'end_date', 'main_image', 'is_fully_booked',
            'can_book', 'is_featured', 'created_at'
        ]
        read_only_fields = ['id', 'current_bookings', 'available_spots', 
                           'is_fully_booked', 'can_book', 'created_at']


class TripDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed trip view"""
    destination = DestinationSerializer(read_only=True)
    available_spots = serializers.ReadOnlyField()
    is_fully_booked = serializers.ReadOnlyField()
    can_book = serializers.ReadOnlyField()
    
    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'destination', 'description', 'trip_type',
            'duration_days', 'price', 'max_capacity', 'current_bookings',
            'available_spots', 'start_date', 'end_date', 'main_image',
            'gallery', 'is_active', 'is_featured', 'is_fully_booked',
            'can_book', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'current_bookings', 'available_spots',
                           'is_fully_booked', 'can_book', 'created_at', 'updated_at']


class TripCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new trips (admin only)"""
    
    class Meta:
        model = Trip
        fields = [
            'title', 'destination', 'description', 'trip_type',
            'duration_days', 'price', 'max_capacity', 'start_date',
            'end_date', 'main_image', 'gallery', 'is_active', 'is_featured'
        ]
    
    def validate(self, data):
        """Validate trip dates and capacity"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        max_capacity = data.get('max_capacity')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise serializers.ValidationError(
                    "End date must be after start date"
                )
            
            if start_date < timezone.now().date():
                raise serializers.ValidationError(
                    "Start date cannot be in the past"
                )
        
        if max_capacity and max_capacity <= 0:
            raise serializers.ValidationError(
                "Maximum capacity must be greater than 0"
            )
        
        return data


class TripUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating trips (admin only)"""
    
    class Meta:
        model = Trip
        fields = [
            'title', 'destination', 'description', 'trip_type',
            'duration_days', 'price', 'max_capacity', 'start_date',
            'end_date', 'main_image', 'gallery', 'is_active', 'is_featured'
        ]
    
    def validate(self, data):
        """Validate trip updates"""
        # Check if trying to reduce capacity below current bookings
        if 'max_capacity' in data:
            current_bookings = self.instance.current_bookings
            if data['max_capacity'] < current_bookings:
                raise serializers.ValidationError(
                    f"Cannot reduce capacity below current bookings ({current_bookings})"
                )
        
        return data
