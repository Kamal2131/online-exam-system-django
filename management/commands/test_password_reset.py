from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from users.models import User

class Command(BaseCommand):
    help = 'Test password reset email functionality'
    
    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to test with')
    
    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"Testing password reset for: {user.email}")
            
            # Generate a reset token (simplified version)
            from django.utils.crypto import get_random_string
            reset_token = get_random_string(50)
            user.password_reset_token = reset_token
            user.save()
            
            # Create reset URL
            reset_url = f"http://localhost:8000/api/users/password-reset-confirm/{reset_token}/"
            
            # Send email
            send_mail(
                'Password Reset Test',
                f'Click here to reset your password: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f"Password reset email sent to {user.email}")
            )
            self.stdout.write(f"Reset URL: {reset_url}")
            self.stdout.write(f"Reset token: {reset_token}")
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"User '{username}' not found")
            )