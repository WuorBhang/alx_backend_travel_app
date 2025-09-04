# ALX Travel App Backend

A comprehensive travel booking platform API built with Django REST Framework, featuring full Swagger/OpenAPI documentation and ready for deployment on Render.

## 🚀 Features

- **User Authentication & Management**: Registration, login, profile management
- **Trip Management**: Browse, search, and filter travel packages
- **Booking System**: Create, manage, and track bookings
- **Admin Panel**: Full administrative interface
- **API Documentation**: Interactive Swagger UI and ReDoc
- **Production Ready**: Configured for Render deployment

## 📚 API Documentation

Once deployed, access the interactive API documentation at:
- **Swagger UI**: `https://your-app.onrender.com/swagger/`
- **ReDoc**: `https://your-app.onrender.com/redoc/`
- **JSON Schema**: `https://your-app.onrender.com/swagger.json`

## 🛠 Local Development Setup

### Prerequisites
- Python 3.8+
- PostgreSQL (for production) or SQLite (for development)
- Virtual environment

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd alx_backend_travel_app
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000/swagger/` to access the API documentation.

## 🌐 Deployment on Render

Follow the detailed [Deployment Guide](DEPLOYMENT_GUIDE.md) for step-by-step instructions.

### Quick Deployment Steps

1. **Create PostgreSQL Database on Render**
2. **Create Web Service on Render**
3. **Configure Environment Variables**
4. **Deploy**

### Required Environment Variables
```bash
SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com,*.onrender.com
DATABASE_URL=postgresql://username:password@host:port/database
```

## 📖 API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout
- `POST /api/v1/auth/change-password/` - Change password

### Trips
- `GET /api/v1/trips/` - List trips (with filtering)
- `GET /api/v1/trips/featured/` - Featured trips
- `GET /api/v1/trips/search/?q=query` - Search trips
- `GET /api/v1/trips/{id}/availability/` - Trip availability

### Bookings
- `POST /api/v1/bookings/` - Create booking
- `GET /api/v1/bookings/my_bookings/` - User's bookings
- `POST /api/v1/bookings/{id}/cancel/` - Cancel booking
- `GET /api/v1/bookings/upcoming/` - Upcoming bookings

### User Management
- `GET /api/v1/users/me/` - Get user info
- `GET /api/v1/profiles/me/` - Get user profile
- `PUT /api/v1/profiles/update_me/` - Update profile

## 🔧 Project Structure

```
alx_backend_travel_app/
├── alx_travel_app/          # Main Django project
│   ├── settings.py          # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── bookings/               # Booking management app
│   ├── models.py           # Booking models
│   ├── views.py            # API views
│   ├── serializers.py      # DRF serializers
│   └── urls.py             # App URLs
├── trips/                  # Trip management app
│   ├── models.py           # Trip and destination models
│   ├── views.py            # API views
│   ├── serializers.py      # DRF serializers
│   └── urls.py             # App URLs
├── users/                  # User management app
│   ├── models.py           # User profile models
│   ├── views.py            # API views
│   ├── serializers.py      # DRF serializers
│   └── urls.py             # App URLs
├── requirements.txt        # Python dependencies
├── build.sh               # Render build script
├── .env                   # Environment variables
└── manage.py              # Django management script
```

## 🔐 Authentication

The API uses Token-based authentication. Include the token in requests:

```bash
curl -H "Authorization: Token your_token_here" \
     https://your-app.onrender.com/api/v1/trips/
```

## 📊 API Features

### Filtering & Search
- **Trips**: Filter by type, destination, price range, dates
- **Bookings**: Filter by status, trip type
- **Search**: Full-text search across trips and destinations

### Pagination
All list endpoints support pagination:
- `page`: Page number
- `page_size`: Items per page (default: 20)

### Response Format
```json
{
  "count": 100,
  "next": "https://api.example.com/trips/?page=3",
  "previous": "https://api.example.com/trips/?page=1",
  "results": [...]
}
```

## 🧪 Testing

Run tests with:
```bash
python manage.py test
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support and questions:
- Email: uhuribhang211@gmail.com
- Documentation: [API Documentation](api_documentation.md)
- Deployment Guide: [Deployment Guide](DEPLOYMENT_GUIDE.md)

## 🔄 Version History

- **v1.0.0**: Initial release with full API documentation and Render deployment support

---

**Note**: Make sure to activate your virtual environment before running Django commands:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
