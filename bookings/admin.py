from django.contrib import admin
from .models import Booking, BookingHistory


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'trip', 'number_of_people', 'total_price',
        'status', 'booking_date', 'is_active'
    ]
    list_filter = [
        'status', 'booking_date', 'trip__trip_type', 'trip__destination__country'
    ]
    search_fields = [
        'user__username', 'user__email', 'trip__title', 'trip__destination__name'
    ]
    list_editable = ['status']
    readonly_fields = [
        'total_price', 'booking_date', 'confirmation_date', 
        'cancellation_date', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'trip')
        }),
        ('Booking Details', {
            'fields': ('number_of_people', 'total_price', 'status')
        }),
        ('Dates', {
            'fields': ('booking_date', 'confirmation_date', 'cancellation_date')
        }),
        ('Contact & Requests', {
            'fields': ('special_requests', 'contact_phone', 'contact_email')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Show all bookings with related data"""
        return super().get_queryset(request).select_related(
            'user', 'trip', 'trip__destination'
        )


@admin.register(BookingHistory)
class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'booking', 'old_status', 'new_status', 
        'changed_by', 'changed_at'
    ]
    list_filter = ['new_status', 'changed_at', 'changed_by']
    search_fields = [
        'booking__user__username', 'booking__trip__title', 'change_reason'
    ]
    readonly_fields = ['changed_at']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking', 'old_status', 'new_status')
        }),
        ('Change Details', {
            'fields': ('changed_by', 'change_reason', 'changed_at')
        }),
    )
    
    def get_queryset(self, request):
        """Show all history with related data"""
        return super().get_queryset(request).select_related(
            'booking', 'booking__user', 'booking__trip', 'changed_by'
        )
