from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import UserProfile
from .serializers import (
    UserSerializer, UserProfileSerializer, UserProfileUpdateSerializer,
    UserRegistrationSerializer, UserUpdateSerializer, ChangePasswordSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)


@swagger_auto_schema(
    method='post',
    operation_description="Register a new user account",
    request_body=UserRegistrationSerializer,
    responses={
        201: UserSerializer,
        400: openapi.Response('Bad Request', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
        ))
    }
)
class UserRegistrationView(generics.CreateAPIView):
    """User registration view"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserLoginView(ObtainAuthToken):
    """Custom login view that returns user data with token"""
    
    @swagger_auto_schema(
        operation_description="Login user and return authentication token with user data",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['username', 'password']
        ),
        responses={
            200: openapi.Response('Login Success', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': UserSerializer,
                    'profile': UserProfileSerializer
                }
            )),
            400: openapi.Response('Bad Request', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
            ))
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'profile': UserProfileSerializer(user.profile).data
        })


class UserLogoutView(generics.GenericAPIView):
    """User logout view"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Logout user and delete authentication token",
        responses={
            200: openapi.Response('Logout Success', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
            )),
            500: openapi.Response('Internal Server Error', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
            ))
        }
    )
    def post(self, request):
        try:
            # Delete the token
            request.user.auth_token.delete()
            logout(request)
            return Response({'message': 'Successfully logged out'})
        except Exception as e:
            return Response(
                {'error': 'Error during logout'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user profile management
    
    Allows users to view and update their own profile information.
    Users can only access their own profile data.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Users can only access their own profile"""
        return UserProfile.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['update', 'partial_update']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer
    
    def get_object(self):
        """Get current user's profile"""
        return self.request.user.profile
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get current user's profile information",
        responses={200: UserProfileSerializer}
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        methods=['put', 'patch'],
        operation_description="Update current user's profile information",
        request_body=UserProfileUpdateSerializer,
        responses={
            200: UserProfileUpdateSerializer,
            400: openapi.Response('Bad Request', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
            ))
        }
    )
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """Update current user's profile"""
        profile = request.user.profile
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user information (read-only)
    
    Provides read-only access to user information.
    Users can only access their own user data.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Users can only access their own information"""
        return User.objects.filter(id=self.request.user.id)
    
    serializer_class = UserSerializer
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get current user's basic information",
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's information"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        methods=['put', 'patch'],
        operation_description="Update current user's basic information",
        request_body=UserUpdateSerializer,
        responses={
            200: UserUpdateSerializer,
            400: openapi.Response('Bad Request', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
            ))
        }
    )
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """Update current user's information"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.GenericAPIView):
    """Change password view"""
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    @swagger_auto_schema(
        operation_description="Change user password",
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response('Password Changed', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'token': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: openapi.Response('Bad Request', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
            ))
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Delete old token and create new one
            Token.objects.filter(user=user).delete()
            new_token = Token.objects.create(user=user)
            
            return Response({
                'message': 'Password changed successfully',
                'token': new_token.key
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(generics.GenericAPIView):
    """Password reset request view"""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer
    
    @swagger_auto_schema(
        operation_description="Request password reset for a user account",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: openapi.Response('Reset Request Sent', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
            )),
            400: openapi.Response('Bad Request', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
            ))
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # In a real application, you would send an email with reset link
            # For now, we'll just return a success message
            return Response({
                'message': f'Password reset instructions sent to {email}'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(generics.GenericAPIView):
    """Password reset confirmation view"""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    @swagger_auto_schema(
        operation_description="Confirm password reset with token",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: openapi.Response('Password Reset Success', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
            )),
            400: openapi.Response('Bad Request', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'error': openapi.Schema(type=openapi.TYPE_STRING)}
            ))
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # In a real application, you would validate the token
            # For now, we'll just return a success message
            return Response({
                'message': 'Password reset successfully'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
