#Import dependencies
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

User = get_user_model()

@extend_schema(
    request=UserLoginSerializer,
    responses={200: OpenApiTypes.OBJECT},
    examples=[
        OpenApiExample(
            'Login Example',
            value={
                'username': 'teststudent',
                'password': 'testpass123'
            }
        )
    ]
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_login(request):
    serializer = UserLoginSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Serialize user data
        user_data = UserProfileSerializer(user).data
        
        # Optional: Create session for browser-based access
        if request.data.get('remember_me'):
            # Set session to expire in 2 weeks if remember me is checked
            request.session.set_expiry(1209600)  # 2 weeks in seconds
        else:
            # Browser session length (until browser is closed)
            request.session.set_expiry(0)
            
        login(request, user)  # Optional: for session-based auth
        
        return Response({
            'user': user_data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def user_profile(request):
    user = request.user
    serializer = UserProfileSerializer(user)
    return Response(serializer.data)

@api_view(['POST'])
def user_logout(request):
    # For JWT, client should simply discard the token
    # For session auth, we can log out
    from django.contrib.auth import logout
    logout(request)
    return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_request(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        # Generate reset token
        reset_token = get_random_string(50)
        user.password_reset_token = reset_token
        user.password_reset_expires = timezone.now() + timedelta(hours=1)
        user.save()
        
        # Send email (in production, use Celery for async)
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token}/"
        send_mail(
            'Password Reset Request',
            f'Click here to reset your password: {reset_url}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        return Response({"detail": "Password reset email sent."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        # Don't reveal whether email exists
        return Response({"detail": "If this email exists, we've sent a password reset link."}, 
                       status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def password_reset_confirm(request, token):
    new_password = request.data.get('new_password')
    try:
        user = User.objects.get(
            password_reset_token=token,
            password_reset_expires__gt=timezone.now()
        )
        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.save()
        return Response({"detail": "Password reset successful."}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "Invalid or expired reset token."}, 
                       status=status.HTTP_400_BAD_REQUEST)
        

# In users/views.py
import os
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def view_sent_emails(request):
    if hasattr(settings, 'EMAIL_FILE_PATH'):
        email_dir = settings.EMAIL_FILE_PATH
        emails = []
        if os.path.exists(email_dir):
            for filename in os.listdir(email_dir):
                if filename.endswith('.log'):
                    with open(os.path.join(email_dir, filename), 'r') as f:
                        content = f.read()
                        emails.append({
                            'filename': filename,
                            'content': content
                        })
        return Response({'emails': emails})
    return Response({'error': 'File email backend not configured'})