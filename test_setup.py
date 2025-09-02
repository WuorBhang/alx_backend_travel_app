#!/usr/bin/env python3
"""
Simple test script to verify ALX Travel App setup
Run this after completing the installation to test basic functionality
"""

import os
import sys
import django
from pathlib import Path

def test_django_setup():
    """Test if Django is properly configured"""
    print("🧪 Testing Django setup...")
    
    try:
        # Add project directory to Python path
        project_dir = Path(__file__).resolve().parent
        sys.path.insert(0, str(project_dir))
        
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')
        
        # Configure Django
        django.setup()
        
        print("✅ Django setup successful!")
        return True
        
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def test_models():
    """Test if models can be imported"""
    print("🗄️ Testing models...")
    
    try:
        from trips.models import Trip, Destination
        from bookings.models import Booking, BookingHistory
        from users.models import UserProfile
        
        print("✅ All models imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False

def test_serializers():
    """Test if serializers can be imported"""
    print("📝 Testing serializers...")
    
    try:
        from trips.serializers import TripListSerializer, DestinationSerializer
        from bookings.serializers import BookingListSerializer
        from users.serializers import UserSerializer
        
        print("✅ All serializers imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Serializer import failed: {e}")
        return False

def test_views():
    """Test if views can be imported"""
    print("👁️ Testing views...")
    
    try:
        from trips.views import TripViewSet, DestinationViewSet
        from bookings.views import BookingViewSet
        from users.views import UserViewSet
        
        print("✅ All views imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ View import failed: {e}")
        return False

def test_celery():
    """Test if Celery can be imported"""
    print("🐌 Testing Celery...")
    
    try:
        from alx_travel_app.celery import app
        from bookings.tasks import send_booking_confirmation_email
        
        print("✅ Celery setup successful!")
        return True
        
    except Exception as e:
        print(f"❌ Celery setup failed: {e}")
        return False

def test_urls():
    """Test if URLs can be imported"""
    print("🔗 Testing URLs...")
    
    try:
        from alx_travel_app.urls import urlpatterns
        
        print("✅ URL configuration loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ URL configuration failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ALX Travel App - System Test")
    print("=" * 50)
    
    tests = [
        test_django_setup,
        test_models,
        test_serializers,
        test_views,
        test_celery,
        test_urls,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your ALX Travel App is ready to use.")
        print("\n🚀 Next steps:")
        print("1. Run: python manage.py makemigrations")
        print("2. Run: python manage.py migrate")
        print("3. Run: python manage.py createsuperuser")
        print("4. Run: python manage.py runserver")
        print("5. Visit: http://localhost:8000/swagger/")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("💡 Make sure you have:")
        print("   - Installed all requirements: pip install -r requirements.txt")
        print("   - Set up your .env file")
        print("   - Run database migrations")

if __name__ == "__main__":
    main()
