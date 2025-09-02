# 🌍 ALX Travel App

A modern, robust travel booking platform backend system built with Django REST Framework. This project enables users to discover exciting destinations and seamlessly book trips online through a secure, scalable, and automated API.

## 🎯 Features

- **Trip Listings**: Browse curated travel packages with detailed information
- **Smart Booking System**: Real-time reservation with capacity tracking and overbooking prevention
- **User Accounts**: Secure registration, login, and profile management
- **Automated Email Notifications**: Instant confirmations using Celery background tasks
- **Public API Documentation**: Interactive Swagger UI for developers and testers
- **Production-Ready Deployment**: Fully deployed with environment security and scalable architecture

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (for production) or SQLite (for development)
- Redis (for Celery)
- Virtual environment tool (venv or virtualenv)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd alx_backend_travel_app
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Start Celery worker (in new terminal)**
   ```bash
   celery -A alx_travel_app worker -l info
   ```

9. **Start Celery beat scheduler (in new terminal)**
   ```bash
   celery -A alx_travel_app beat -l info
   ```

### Using Docker

1. **Build and start services**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## 🌐 API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `POST /api/v1/auth/change-password/` - Change password
- `POST /api/v1/auth/reset-password/` - Request password reset
- `POST /api/v1/auth/reset-password/confirm/` - Confirm password reset

### Trips
- `GET /api/v1/trips/` - List all trips
- `GET /api/v1/trips/{id}/` - Get trip details
- `GET /api/v1/trips/featured/` - Get featured trips
- `GET /api/v1/trips/upcoming/` - Get upcoming trips
- `GET /api/v1/trips/search/?q={query}` - Search trips
- `GET /api/v1/trips/{id}/availability/` - Check trip availability

### Destinations
- `GET /api/v1/destinations/` - List all destinations
- `GET /api/v1/destinations/{id}/` - Get destination details

### Bookings
- `GET /api/v1/bookings/` - List user's bookings
- `POST /api/v1/bookings/` - Create new booking
- `GET /api/v1/bookings/{id}/` - Get booking details
- `PUT /api/v1/bookings/{id}/` - Update booking
- `POST /api/v1/bookings/{id}/cancel/` - Cancel booking
- `POST /api/v1/bookings/{id}/confirm/` - Confirm booking
- `GET /api/v1/bookings/my_bookings/` - Get current user's bookings
- `GET /api/v1/bookings/active/` - Get active bookings
- `GET /api/v1/bookings/upcoming/` - Get upcoming bookings
- `GET /api/v1/bookings/past/` - Get past bookings

### User Profile
- `GET /api/v1/profiles/me/` - Get current user's profile
- `PUT /api/v1/profiles/me/` - Update current user's profile
- `GET /api/v1/users/me/` - Get current user's information
- `PUT /api/v1/users/me/` - Update current user's information

## 📚 API Documentation

Access the interactive Swagger documentation at:
- **Swagger UI**: `/swagger/`
- **ReDoc**: `/redoc/`

## 🗄️ Database Models

### Trip
- Basic trip information (title, description, type)
- Destination relationship
- Pricing and capacity management
- Date ranges and availability tracking
- Image and gallery support

### Destination
- Location details (name, country, description)
- Image support
- Metadata tracking

### Booking
- User and trip relationships
- Booking details (people count, total price)
- Status management (pending, confirmed, cancelled, completed)
- Special requests and contact information
- Automatic capacity updates

### UserProfile
- Extended user information
- Travel preferences and settings
- Notification preferences
- Contact details

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DB_NAME=alx_travel_db
DB_USER=alx_travel_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

## 🚀 Deployment

### Production Deployment

1. **Set up production server**
   - Use a production-ready server (AWS, DigitalOcean, etc.)
   - Install Python, PostgreSQL, Redis, and Nginx

2. **Configure environment**
   - Set `DEBUG=False`
   - Configure production database
   - Set up SSL certificates
   - Configure email settings

3. **Deploy with Gunicorn**
   ```bash
   gunicorn --bind 0.0.0.0:8000 alx_travel_app.wsgi:application
   ```

4. **Set up Nginx reverse proxy**
   - Configure static file serving
   - Set up SSL termination
   - Configure proxy to Gunicorn

5. **Start Celery services**
   ```bash
   celery -A alx_travel_app worker -l info
   celery -A alx_travel_app beat -l info
   ```

### Using the Build Script

```bash
chmod +x build.sh
./build.sh
```

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```

## 📧 Email Templates

The system includes comprehensive email templates for:
- Booking confirmations
- Status updates
- Trip reminders
- Welcome messages
- Daily summaries

Templates are located in `templates/emails/` and support both HTML and plain text formats.

## 🔒 Security Features

- Token-based authentication
- CORS protection
- CSRF protection
- Secure password validation
- Environment variable configuration
- Admin-only access to sensitive operations

## 📊 Monitoring and Logging

- Celery task monitoring
- Database query optimization
- Error logging and tracking
- Performance metrics

## 🚀 Future Enhancements

- [ ] Online payment integration (Stripe/PayPal)
- [ ] Trip reviews and ratings system
- [ ] Mobile app development
- [ ] Multi-language support
- [ ] Real-time chat support
- [ ] Advanced analytics dashboard
- [ ] Social media integration
- [ ] Loyalty program

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Bhang Wuor** - *Full Stack Developer*

## 🙏 Acknowledgments

- Django and Django REST Framework communities
- ALX Software Engineering program
- Open source contributors

## 📞 Support

For support and questions:
- Email: contact@alx-travel.com
- Documentation: `/swagger/`
- Issues: GitHub Issues

---

**🌍 Travel begins with a single click. We built the engine behind it.**
