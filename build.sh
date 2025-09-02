#!/bin/bash

# ALX Travel App Build Script
# This script sets up the production environment

echo "🚀 Starting ALX Travel App build process..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one based on env.example"
    echo "📝 Copy env.example to .env and update the values"
    cp env.example .env
    echo "✅ .env file created. Please update the values before continuing."
    exit 1
fi

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found. Please create one manually with:')
    print('python manage.py createsuperuser')
else:
    print('Superuser already exists')
"

# Run tests
echo "🧪 Running tests..."
python manage.py test

echo "✅ Build process completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Update your .env file with production values"
echo "2. Start the Django server: python manage.py runserver"
echo "3. Start Celery worker: celery -A alx_travel_app worker -l info"
echo "4. Start Celery beat: celery -A alx_travel_app beat -l info"
echo ""
echo "🌐 Access your app at: http://localhost:8000"
echo "📚 API Documentation at: http://localhost:8000/swagger/"
echo "🔐 Admin panel at: http://localhost:8000/admin/"
