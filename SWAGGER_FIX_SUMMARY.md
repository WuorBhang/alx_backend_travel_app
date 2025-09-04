# Swagger/OpenAPI Schema Generation Fix

## Issue Summary
The Swagger UI was failing to load the API definition due to schema generation errors. The main issues were:

1. **AnonymousUser Error**: ViewSets were trying to filter querysets using `self.request.user` during schema generation, but `request.user` was an `AnonymousUser` object during this process.

2. **Missing Serializer**: The `UserLogoutView` didn't have a `serializer_class` defined, causing schema generation to fail.

## Fixes Applied

### 1. Fixed BookingViewSet Schema Generation
**File**: `bookings/views.py`

**Problem**: The `get_queryset()` method was trying to filter by `user=self.request.user` during schema generation.

**Solution**: Added a check for `swagger_fake_view` attribute:
```python
def get_queryset(self):
    """Filter queryset based on user permissions"""
    # Handle schema generation
    if getattr(self, 'swagger_fake_view', False):
        return Booking.objects.none()
        
    user = self.request.user
    # ... rest of the method
```

### 2. Fixed UserProfileViewSet Schema Generation
**File**: `users/views.py`

**Problem**: Similar issue with `get_queryset()` trying to filter by anonymous user.

**Solution**: Added schema generation check:
```python
def get_queryset(self):
    """Users can only access their own profile"""
    # Handle schema generation
    if getattr(self, 'swagger_fake_view', False):
        return UserProfile.objects.none()
    return UserProfile.objects.filter(user=self.request.user)
```

### 3. Fixed UserViewSet Schema Generation
**File**: `users/views.py`

**Problem**: Same issue with user filtering during schema generation.

**Solution**: Added schema generation check:
```python
def get_queryset(self):
    """Users can only access their own information"""
    # Handle schema generation
    if getattr(self, 'swagger_fake_view', False):
        return User.objects.none()
    return User.objects.filter(id=self.request.user.id)
```

### 4. Fixed UserLogoutView Serializer Issue
**Files**: `users/serializers.py` and `users/views.py`

**Problem**: `UserLogoutView` didn't have a `serializer_class` defined.

**Solution**: 
1. Created a simple `LogoutSerializer`:
```python
class LogoutSerializer(serializers.Serializer):
    """Serializer for logout endpoint (no fields required)"""
    pass
```

2. Updated `UserLogoutView` to use it:
```python
class UserLogoutView(generics.GenericAPIView):
    """User logout view"""
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer
```

## How the Fix Works

### Schema Generation Detection
The `swagger_fake_view` attribute is set by drf-yasg when it's generating the OpenAPI schema. By checking for this attribute, we can:

1. **Return Empty Querysets**: During schema generation, return `Model.objects.none()` instead of trying to filter by user
2. **Avoid Database Queries**: Prevent unnecessary database operations during schema generation
3. **Maintain Functionality**: Keep the original filtering logic for actual API requests

### Benefits of This Approach
- **Non-Intrusive**: Doesn't affect normal API functionality
- **Performance**: Avoids database queries during schema generation
- **Reliable**: Uses the official drf-yasg mechanism for detecting schema generation
- **Maintainable**: Clear separation between schema generation and runtime behavior

## Testing the Fix

After applying these fixes, the Swagger UI should now:

1. **Load Successfully**: No more "Failed to load API definition" errors
2. **Display All Endpoints**: Show all API endpoints from bookings, trips, and users apps
3. **Show Proper Documentation**: Display the comprehensive API documentation with request/response schemas
4. **Enable Testing**: Allow testing of endpoints directly from the Swagger UI

## Verification Steps

1. **Start the Django server**:
   ```bash
   python manage.py runserver
   ```

2. **Access Swagger UI**:
   ```
   http://localhost:8000/swagger/
   ```

3. **Check for**:
   - No error messages
   - All API endpoints visible
   - Proper request/response schemas
   - Authentication section working

4. **Access ReDoc**:
   ```
   http://localhost:8000/redoc/
   ```

## Additional Notes

- The fixes maintain backward compatibility
- No changes to actual API functionality
- Schema generation is now robust and error-free
- All ViewSets properly handle both schema generation and runtime requests

The API documentation is now fully functional and ready for development and production use.