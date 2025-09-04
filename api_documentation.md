# ALX Travel App API Documentation

## Overview
The ALX Travel App API is a comprehensive travel booking platform that provides endpoints for managing trips, bookings, and user accounts. The API is built using Django REST Framework and includes full Swagger/OpenAPI documentation.

## Base URL
- **Production**: `https://alx-backend-travel-app.onrender.com/api/v1/`
- **Development**: `http://localhost:8000/api/v1/`

## Documentation URLs
- **Swagger UI**: `/swagger/`
- **ReDoc**: `/redoc/`

## Authentication
The API uses Token-based authentication. Include the token in the Authorization header:
```
Authorization: Token your_token_here
```

## API Endpoints

### Authentication Endpoints
- `POST /api/v1/auth/register/` - Register a new user
- `POST /api/v1/auth/login/` - Login and get authentication token
- `POST /api/v1/auth/logout/` - Logout and invalidate token
- `POST /api/v1/auth/change-password/` - Change user password
- `POST /api/v1/auth/reset-password/` - Request password reset
- `POST /api/v1/auth/reset-password/confirm/` - Confirm password reset

### User Management
- `GET /api/v1/users/me/` - Get current user information
- `PUT/PATCH /api/v1/users/update_me/` - Update current user information
- `GET /api/v1/profiles/me/` - Get current user profile
- `PUT/PATCH /api/v1/profiles/update_me/` - Update current user profile

### Trips
- `GET /api/v1/trips/` - List all trips (with filtering and search)
- `POST /api/v1/trips/` - Create new trip (admin only)
- `GET /api/v1/trips/{id}/` - Get trip details
- `PUT/PATCH /api/v1/trips/{id}/` - Update trip (admin only)
- `DELETE /api/v1/trips/{id}/` - Delete trip (admin only)

#### Trip Custom Actions
- `GET /api/v1/trips/featured/` - Get featured trips
- `GET /api/v1/trips/upcoming/` - Get upcoming trips
- `GET /api/v1/trips/search/?q=query` - Search trips
- `GET /api/v1/trips/{id}/availability/` - Get trip availability
- `GET /api/v1/trips/by_destination/?destination_id=1` - Filter by destination
- `GET /api/v1/trips/by_type/?type=adventure` - Filter by trip type
- `GET /api/v1/trips/statistics/` - Get trip statistics (admin only)
- `POST /api/v1/trips/{id}/toggle_featured/` - Toggle featured status (admin only)
- `POST /api/v1/trips/{id}/toggle_active/` - Toggle active status (admin only)

### Destinations
- `GET /api/v1/destinations/` - List all destinations
- `GET /api/v1/destinations/{id}/` - Get destination details

### Bookings
- `GET /api/v1/bookings/` - List user's bookings
- `POST /api/v1/bookings/` - Create new booking
- `GET /api/v1/bookings/{id}/` - Get booking details
- `PUT/PATCH /api/v1/bookings/{id}/` - Update booking
- `DELETE /api/v1/bookings/{id}/` - Delete booking (admin only)

#### Booking Custom Actions
- `GET /api/v1/bookings/my_bookings/` - Get current user's bookings
- `GET /api/v1/bookings/active/` - Get active bookings
- `GET /api/v1/bookings/upcoming/` - Get upcoming bookings
- `GET /api/v1/bookings/past/` - Get past bookings
- `POST /api/v1/bookings/{id}/cancel/` - Cancel booking
- `POST /api/v1/bookings/{id}/confirm/` - Confirm booking
- `POST /api/v1/bookings/{id}/update_status/` - Update booking status (admin only)
- `GET /api/v1/bookings/{id}/history/` - Get booking history

### Booking History (Admin Only)
- `GET /api/v1/booking-history/` - List all booking history records

## Query Parameters

### Trips Filtering
- `trip_type` - Filter by trip type (adventure, cultural, relaxation, business, family, romantic)
- `destination` - Filter by destination ID
- `is_featured` - Filter featured trips (true/false)
- `start_date` - Filter by start date (YYYY-MM-DD)
- `end_date` - Filter by end date (YYYY-MM-DD)
- `min_price` - Minimum price filter
- `max_price` - Maximum price filter
- `min_duration` - Minimum duration in days
- `max_duration` - Maximum duration in days
- `available_only` - Show only available trips (true/false)
- `search` - Search in title, description, destination name/country
- `ordering` - Order by price, start_date, duration_days, created_at

### Bookings Filtering
- `status` - Filter by booking status (pending, confirmed, cancelled, completed)
- `trip` - Filter by trip ID
- `trip__trip_type` - Filter by trip type
- `search` - Search in trip title, destination name
- `ordering` - Order by booking_date, total_price, created_at

## Response Formats

### Success Response
```json
{
  "id": 1,
  "field1": "value1",
  "field2": "value2"
}
```

### Error Response
```json
{
  "error": "Error message",
  "details": "Additional error details"
}
```

### Validation Error Response
```json
{
  "field_name": ["Error message for this field"],
  "non_field_errors": ["General validation errors"]
}
```

## Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Rate Limiting
The API implements rate limiting to prevent abuse. Current limits:
- Authenticated users: 1000 requests per hour
- Anonymous users: 100 requests per hour

## Pagination
List endpoints support pagination with the following parameters:
- `page` - Page number
- `page_size` - Number of items per page (default: 20, max: 100)

Response includes pagination metadata:
```json
{
  "count": 100,
  "next": "http://api.example.com/trips/?page=3",
  "previous": "http://api.example.com/trips/?page=1",
  "results": [...]
}
```

## Examples

### Register a new user
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

### Get trips with filtering
```bash
curl -X GET "http://localhost:8000/api/v1/trips/?trip_type=adventure&min_price=100&max_price=1000" \
  -H "Authorization: Token your_token_here"
```

### Create a booking
```bash
curl -X POST http://localhost:8000/api/v1/bookings/ \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "trip": 1,
    "number_of_people": 2,
    "special_requests": "Vegetarian meals please",
    "contact_phone": "+1234567890",
    "contact_email": "john@example.com"
  }'
```

## Deployment on Render

### Environment Variables Required
- `SECRET_KEY` - Django secret key
- `DEBUG` - Set to False for production
- `ALLOWED_HOSTS` - Include your Render domain
- `DB_NAME` - PostgreSQL database name
- `DB_USER` - PostgreSQL username
- `DB_PASSWORD` - PostgreSQL password
- `DB_HOST` - PostgreSQL host
- `DB_PORT` - PostgreSQL port (usually 5432)
- `ADMIN_EMAIL` - Admin user email (optional)
- `ADMIN_PASSWORD` - Admin user password (optional)

### Build Command
```bash
./build.sh
```

### Start Command
```bash
gunicorn alx_travel_app.wsgi:application
```

## Support
For API support and questions, please contact: uhuribhang211@gmail.com