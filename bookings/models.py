from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class Booking(models.Model):
    """Model for trip bookings"""
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    trip = models.ForeignKey('trips.Trip', on_delete=models.CASCADE, related_name='bookings')
    
    # Booking details
    number_of_people = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of people for this booking"
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status and dates
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    booking_date = models.DateTimeField(auto_now_add=True)
    confirmation_date = models.DateTimeField(null=True, blank=True)
    cancellation_date = models.DateTimeField(null=True, blank=True)
    
    # Special requests
    special_requests = models.TextField(blank=True)
    
    # Contact information
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-booking_date']
        unique_together = ['user', 'trip', 'booking_date']

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} for {self.trip.title}"

    def save(self, *args, **kwargs):
        """Override save to handle booking status changes and trip capacity"""
        is_new = self.pk is None
        old_status = None
        
        if not is_new:
            try:
                old_instance = Booking.objects.get(pk=self.pk)
                old_status = old_instance.status
            except Booking.DoesNotExist:
                pass
        
        # Calculate total price if not set
        if not self.total_price:
            self.total_price = self.trip.price * self.number_of_people
        
        # Handle status changes
        if self.status == 'confirmed' and old_status != 'confirmed':
            self.confirmation_date = timezone.now()
        elif self.status == 'cancelled' and old_status != 'cancelled':
            self.cancellation_date = timezone.now()
        
        super().save(*args, **kwargs)
        
        # Update trip capacity
        if is_new or old_status != self.status:
            self._update_trip_capacity(old_status, self.status)

    def _update_trip_capacity(self, old_status, new_status):
        """Update trip capacity based on booking status changes"""
        trip = self.trip
        
        # If this is a new confirmed booking
        if new_status == 'confirmed' and old_status != 'confirmed':
            trip.current_bookings += self.number_of_people
        # If booking was cancelled
        elif new_status == 'cancelled' and old_status == 'confirmed':
            trip.current_bookings -= self.number_of_people
        # If status changed from cancelled back to confirmed
        elif new_status == 'confirmed' and old_status == 'cancelled':
            trip.current_bookings += self.number_of_people
        
        trip.save()

    @property
    def can_cancel(self):
        """Check if booking can be cancelled"""
        return (
            self.status in ['pending', 'confirmed'] and
            self.trip.start_date > timezone.now().date()
        )

    @property
    def is_active(self):
        """Check if booking is active"""
        return self.status in ['pending', 'confirmed']

    def cancel_booking(self):
        """Cancel the booking if possible"""
        if self.can_cancel:
            self.status = 'cancelled'
            self.save()
            return True
        return False

    def confirm_booking(self):
        """Confirm the booking"""
        if self.status == 'pending':
            self.status = 'confirmed'
            self.save()
            return True
        return False


class BookingHistory(models.Model):
    """Model to track booking status changes"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='history')
    old_status = models.CharField(max_length=20, choices=Booking.BOOKING_STATUS, null=True, blank=True)
    new_status = models.CharField(max_length=20, choices=Booking.BOOKING_STATUS)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    change_reason = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Booking histories'

    def __str__(self):
        return f"{self.booking} - {self.old_status} → {self.new_status}"
