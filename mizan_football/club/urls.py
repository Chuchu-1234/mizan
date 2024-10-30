from django.urls import path
from .views import RegisterView, LoginView, PasswordResetView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
]