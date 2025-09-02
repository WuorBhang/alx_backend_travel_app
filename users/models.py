from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal information
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Travel preferences
    preferred_trip_types = models.JSONField(
        default=list, 
        blank=True,
        help_text="List of preferred trip types (e.g., ['adventure', 'cultural'])"
    )
    preferred_destinations = models.JSONField(
        default=list, 
        blank=True,
        help_text="List of preferred destination countries"
    )
    budget_range = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low ($0 - $1000)'),
            ('medium', 'Medium ($1000 - $5000)'),
            ('high', 'High ($5000+)'),
        ],
        blank=True
    )
    
    # Profile settings
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

    @property
    def has_complete_profile(self):
        """Check if profile has essential information"""
        return bool(
            self.phone_number and 
            self.address and 
            self.city and 
            self.country
        )


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when a new user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
