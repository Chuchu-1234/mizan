from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm

from .serializers import RegisterSerializer, UserSerializer

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView


from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        token, created = Token.objects.get_or_create(user=response.data['id'])
        response.data['token'] = token.key
        return response

class LoginView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the email and send the password reset link
        users = User.objects.filter(email=email)
        if not users.exists():
            return Response({"error": "No user with this email found."}, status=status.HTTP_404_NOT_FOUND)
        
        for user in users:
            # Generate password reset link
            context = {
                "email": user.email,
                "domain": request.get_host(),
                "site_name": "Your Site",
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": default_token_generator.make_token(user),
                "protocol": "https" if request.is_secure() else "http",
            }

            # Render email content with reset link
            email_subject = "Password Reset Requested"
            email_body = render_to_string("password_reset_email.txt", context)
            
            try:
                send_mail(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email])
            except BadHeaderError:
                return Response({"error": "Invalid header found."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"success": "Password reset link has been sent to your email."}, status=status.HTTP_200_OK)

