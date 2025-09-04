# ALX Travel App - Render Deployment Guide

## Overview
This guide will help you deploy the ALX Travel App backend to Render, a modern cloud platform that provides easy deployment for web applications.

## Prerequisites
- A Render account (sign up at https://render.com)
- Your code pushed to a GitHub repository
- PostgreSQL database (can be created on Render)

## Step 1: Prepare Your Repository

Ensure your repository contains these essential files:
- `requirements.txt` - Python dependencies
- `build.sh` - Build script for Render
- `.env` - Environment variables template
- `manage.py` - Django management script

## Step 2: Create a PostgreSQL Database on Render

1. Log into your Render dashboard
2. Click "New +" and select "PostgreSQL"
3. Configure your database:
   - **Name**: `alx-travel-db`
   - **Database**: `alx_travel_db`
   - **User**: `alx_travel_user`
   - **Region**: Choose closest to your users
   - **PostgreSQL Version**: 15 (recommended)
   - **Plan**: Free tier for development

4. After creation, note down the connection details:
   - **Internal Database URL**: Use this for your Django app
   - **External Database URL**: For external connections

## Step 3: Create a Web Service on Render

1. Click "New +" and select "Web Service"
2. Connect your GitHub repository
3. Configure the service:

### Basic Settings
- **Name**: `alx-backend-travel-app`
- **Region**: Same as your database
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty if Django project is in root

### Build & Deploy Settings
- **Runtime**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn alx_travel_app.wsgi:application`

### Environment Variables
Add these environment variables in the Render dashboard:

```bash
# Django Settings
SECRET_KEY=your_super_secret_key_here_make_it_long_and_random
DEBUG=False
ALLOWED_HOSTS=alx-backend-travel-app.onrender.com,*.onrender.com

# Database (use your PostgreSQL connection details from Step 2)
DATABASE_URL=postgresql://username:password@hostname:port/database_name

# Alternative individual database settings
DB_NAME=alx_travel_db
DB_USER=alx_travel_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=5432

# Security Settings
CSRF_TRUSTED_ORIGINS=https://alx-backend-travel-app.onrender.com,https://your-frontend-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS Settings (adjust for your frontend domain)
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com,http://localhost:3000

# Admin User (optional - for automatic superuser creation)
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=secure_admin_password

# Email Settings (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

## Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Run the build script (`build.sh`)
   - Start your application with gunicorn

## Step 5: Verify Deployment

Once deployed, your API will be available at:
- **Base URL**: `https://alx-backend-travel-app.onrender.com`
- **Swagger Documentation**: `https://alx-backend-travel-app.onrender.com/swagger/`
- **ReDoc Documentation**: `https://alx-backend-travel-app.onrender.com/redoc/`
- **Admin Panel**: `https://alx-backend-travel-app.onrender.com/admin/`

### Test the API
1. Visit the Swagger documentation URL
2. Try the authentication endpoints:
   - Register a new user
   - Login to get a token
   - Use the token to access protected endpoints

## Step 6: Configure Custom Domain (Optional)

If you have a custom domain:
1. Go to your web service settings
2. Click "Custom Domains"
3. Add your domain
4. Update DNS records as instructed
5. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` environment variables

## Environment Variables Reference

### Required Variables
- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DATABASE_URL`: PostgreSQL connection string from Render
- `ALLOWED_HOSTS`: Your Render domain and any custom domains

### Optional Variables
- `DEBUG`: Set to `False` for production (default)
- `ADMIN_EMAIL`: Email for auto-created admin user
- `ADMIN_PASSWORD`: Password for auto-created admin user
- `CORS_ALLOWED_ORIGINS`: Frontend domains that can access your API
- Email settings for password reset functionality

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check that `build.sh` has execute permissions
   - Verify all dependencies are in `requirements.txt`
   - Check build logs for specific error messages

2. **Database Connection Issues**
   - Verify `DATABASE_URL` is correctly set
   - Ensure database and web service are in the same region
   - Check that database is running and accessible

3. **Static Files Not Loading**
   - Ensure `whitenoise` is in `requirements.txt`
   - Verify `STATIC_ROOT` is set correctly in settings
   - Check that `collectstatic` runs successfully in build script

4. **CORS Issues**
   - Update `CORS_ALLOWED_ORIGINS` with your frontend domain
   - Ensure `django-cors-headers` is installed and configured

### Debugging Steps

1. **Check Logs**
   - Go to your web service dashboard
   - Click on "Logs" to see real-time application logs
   - Look for error messages and stack traces

2. **Test Locally**
   - Set up the same environment variables locally
   - Test with PostgreSQL instead of SQLite
   - Ensure everything works before deploying

3. **Database Issues**
   - Connect to your database using the external URL
   - Verify tables are created correctly
   - Check that migrations ran successfully

## Monitoring and Maintenance

### Health Checks
Render automatically monitors your service health. Your app should respond to HTTP requests on the configured port.

### Scaling
- Free tier: Limited resources, may sleep after inactivity
- Paid tiers: Always-on, better performance, custom scaling

### Updates
- Push changes to your GitHub repository
- Render will automatically redeploy
- Monitor logs during deployment

## Security Best Practices

1. **Environment Variables**
   - Never commit sensitive data to your repository
   - Use strong, unique passwords
   - Rotate secrets regularly

2. **Database Security**
   - Use strong database passwords
   - Limit database access to your application only
   - Regular backups (Render provides automatic backups)

3. **Application Security**
   - Keep dependencies updated
   - Use HTTPS only (Render provides SSL certificates)
   - Implement proper authentication and authorization

## API Documentation Access

After deployment, your API documentation will be available at:

- **Swagger UI**: Interactive API documentation with testing capabilities
  - URL: `https://your-app.onrender.com/swagger/`
  - Features: Try out endpoints, view request/response schemas

- **ReDoc**: Clean, responsive API documentation
  - URL: `https://your-app.onrender.com/redoc/`
  - Features: Better for reading, mobile-friendly

- **JSON Schema**: Raw OpenAPI specification
  - URL: `https://your-app.onrender.com/swagger.json`

## Support

If you encounter issues:
1. Check Render's documentation: https://render.com/docs
2. Review application logs in Render dashboard
3. Test locally with production-like settings
4. Contact support: uhuribhang211@gmail.com

## Next Steps

After successful deployment:
1. Set up monitoring and alerting
2. Configure automated backups
3. Set up CI/CD pipeline for automated deployments
4. Implement caching for better performance
5. Set up logging and error tracking