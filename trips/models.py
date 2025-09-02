from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Destination(models.Model):
    """Model for travel destinations"""
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='destinations/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.country}"


class Trip(models.Model):
    """Model for travel trips/packages"""
    TRIP_TYPES = [
        ('adventure', 'Adventure'),
        ('cultural', 'Cultural'),
        ('relaxation', 'Relaxation'),
        ('business', 'Business'),
        ('family', 'Family'),
        ('romantic', 'Romantic'),
    ]
    
    title = models.CharField(max_length=200)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='trips')
    description = models.TextField()
    trip_type = models.CharField(max_length=20, choices=TRIP_TYPES)
    
    # Trip details
    duration_days = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(365)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_capacity = models.PositiveIntegerField()
    current_bookings = models.PositiveIntegerField(default=0)
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Images
    main_image = models.ImageField(upload_to='trips/', blank=True, null=True)
    gallery = models.JSONField(default=list, blank=True)  # List of image URLs
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{self.title} - {self.destination.name}"

    @property
    def available_spots(self):
        """Calculate available spots for booking"""
        return self.max_capacity - self.current_bookings

    @property
    def is_fully_booked(self):
        """Check if trip is fully booked"""
        return self.current_bookings >= self.max_capacity

    @property
    def is_past(self):
        """Check if trip has already passed"""
        return self.end_date < timezone.now().date()

    def can_book(self):
        """Check if trip can be booked"""
        return (
            self.is_active and 
            not self.is_fully_booked and 
            not self.is_past
        )
