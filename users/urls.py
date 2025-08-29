from django.urls import path
from .views import RegisterView, user_login, user_profile, user_logout, password_reset_confirm, password_reset_request, view_sent_emails

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', user_login, name='user-login'),
    path('profile/', user_profile, name='user-profile'),
    path('logout/', user_logout, name='user-logout'),
    path('password-reset/', password_reset_request, name='password-reset'),
    path('password-reset-confirm/<str:token>/', password_reset_confirm, name='password-reset-confirm'),
    path('sent-emails/', view_sent_emails, name='view-sent-emails'),
]