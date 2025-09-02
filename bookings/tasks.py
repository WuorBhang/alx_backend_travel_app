from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import Booking


@shared_task
def send_booking_confirmation_email(booking_id):
    """Send confirmation email for a new booking"""
    try:
        booking = Booking.objects.select_related('user', 'trip', 'trip__destination').get(id=booking_id)
        
        subject = f'Booking Confirmation - {booking.trip.title}'
        
        # Email context
        context = {
            'booking': booking,
            'user': booking.user,
            'trip': booking.trip,
            'destination': booking.trip.destination,
            'booking_date': booking.booking_date.strftime('%B %d, %Y'),
            'trip_start': booking.trip.start_date.strftime('%B %d, %Y'),
            'trip_end': booking.trip.end_date.strftime('%B %d, %Y'),
        }
        
        # Render email templates
        html_message = render_to_string('emails/booking_confirmation.html', context)
        plain_message = render_to_string('emails/booking_confirmation.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return f'Confirmation email sent to {booking.user.email} for booking {booking.id}'
        
    except Booking.DoesNotExist:
        return f'Booking {booking_id} not found'
    except Exception as e:
        return f'Error sending confirmation email: {str(e)}'


@shared_task
def send_booking_status_update_email(booking_id, old_status, new_status):
    """Send email notification for booking status changes"""
    try:
        booking = Booking.objects.select_related('user', 'trip', 'trip__destination').get(id=booking_id)
        
        subject = f'Booking Status Update - {booking.trip.title}'
        
        # Email context
        context = {
            'booking': booking,
            'user': booking.user,
            'trip': booking.trip,
            'destination': booking.trip.destination,
            'old_status': old_status.title(),
            'new_status': new_status.title(),
            'update_date': timezone.now().strftime('%B %d, %Y at %I:%M %p'),
        }
        
        # Render email templates
        html_message = render_to_string('emails/booking_status_update.html', context)
        plain_message = render_to_string('emails/booking_status_update.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return f'Status update email sent to {booking.user.email} for booking {booking.id}'
        
    except Booking.DoesNotExist:
        return f'Booking {booking_id} not found'
    except Exception as e:
        return f'Error sending status update email: {str(e)}'


@shared_task
def send_trip_reminder_email(booking_id):
    """Send reminder email before trip starts"""
    try:
        booking = Booking.objects.select_related('user', 'trip', 'trip__destination').get(id=booking_id)
        
        # Only send reminder for confirmed bookings
        if booking.status != 'confirmed':
            return f'Booking {booking_id} is not confirmed, skipping reminder'
        
        subject = f'Trip Reminder - {booking.trip.title} starts soon!'
        
        # Email context
        context = {
            'booking': booking,
            'user': booking.user,
            'trip': booking.trip,
            'destination': booking.trip.destination,
            'trip_start': booking.trip.start_date.strftime('%B %d, %Y'),
            'trip_end': booking.trip.end_date.strftime('%B %d, %Y'),
            'days_until_trip': (booking.trip.start_date - timezone.now().date()).days,
        }
        
        # Render email templates
        html_message = render_to_string('emails/trip_reminder.html', context)
        plain_message = render_to_string('emails/trip_reminder.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return f'Reminder email sent to {booking.user.email} for trip {booking.trip.id}'
        
    except Booking.DoesNotExist:
        return f'Booking {booking_id} not found'
    except Exception as e:
        return f'Error sending reminder email: {str(e)}'


@shared_task
def send_welcome_email(user_id):
    """Send welcome email to new users"""
    try:
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
        
        subject = 'Welcome to ALX Travel App!'
        
        # Email context
        context = {
            'user': user,
            'welcome_date': timezone.now().strftime('%B %d, %Y'),
        }
        
        # Render email templates
        html_message = render_to_string('emails/welcome.html', context)
        plain_message = render_to_string('emails/welcome.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return f'Welcome email sent to {user.email}'
        
    except User.DoesNotExist:
        return f'User {user_id} not found'
    except Exception as e:
        return f'Error sending welcome email: {str(e)}'


@shared_task
def cleanup_expired_bookings():
    """Clean up expired bookings (past trips)"""
    try:
        expired_bookings = Booking.objects.filter(
            trip__end_date__lt=timezone.now().date(),
            status__in=['pending', 'confirmed']
        )
        
        count = expired_bookings.count()
        expired_bookings.update(status='completed')
        
        return f'Marked {count} expired bookings as completed'
        
    except Exception as e:
        return f'Error cleaning up expired bookings: {str(e)}'


@shared_task
def send_daily_booking_summary():
    """Send daily summary of bookings to admin"""
    try:
        from django.contrib.auth.models import User
        
        # Get today's bookings
        today = timezone.now().date()
        today_bookings = Booking.objects.filter(
            created_at__date=today
        ).select_related('user', 'trip', 'trip__destination')
        
        if not today_bookings.exists():
            return 'No bookings today, skipping summary email'
        
        # Get admin users
        admin_users = User.objects.filter(is_staff=True, is_active=True)
        
        if not admin_users.exists():
            return 'No admin users found for summary email'
        
        subject = f'Daily Booking Summary - {today.strftime("%B %d, %Y")}'
        
        # Email context
        context = {
            'date': today.strftime('%B %d, %Y'),
            'total_bookings': today_bookings.count(),
            'bookings': today_bookings,
            'total_revenue': sum(booking.total_price for booking in today_bookings),
        }
        
        # Render email templates
        html_message = render_to_string('emails/daily_summary.html', context)
        plain_message = render_to_string('emails/daily_summary.txt', context)
        
        # Send to all admin users
        admin_emails = [user.email for user in admin_users]
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html_message,
            fail_silently=False,
        )
        
        return f'Daily summary sent to {len(admin_emails)} admin users'
        
    except Exception as e:
        return f'Error sending daily summary: {str(e)}'
