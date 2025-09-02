from django.contrib import admin
from .models import Trip, Destination


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'created_at']
    list_filter = ['country', 'created_at']
    search_fields = ['name', 'country', 'description']
    ordering = ['name']


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'destination', 'trip_type', 'price', 
        'duration_days', 'start_date', 'end_date', 
        'current_bookings', 'max_capacity', 'is_active', 'is_featured'
    ]
    list_filter = [
        'trip_type', 'is_active', 'is_featured', 'start_date', 
        'destination__country'
    ]
    search_fields = ['title', 'description', 'destination__name']
    list_editable = ['is_active', 'is_featured']
    readonly_fields = ['current_bookings', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'destination', 'description', 'trip_type')
        }),
        ('Trip Details', {
            'fields': ('duration_days', 'price', 'max_capacity', 'current_bookings')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Media', {
            'fields': ('main_image', 'gallery')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Show all trips in admin, not just active ones"""
        return super().get_queryset(request).select_related('destination')
