from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.serializers import MyTokenObtainPairSerializer, UserSerializer


class RegisterAPIView(CreateAPIView):
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(serializer.validated_data['password'])
        user.save()
        try:
            send_verification_email(user)
        except Exception as e:
            print(f"Error sending verification email: {str(e)}")  # 디버깅
        return user


def send_verification_email(user):
    subject = "Verify your email"
    message = f"Please verify your email. User ID: {user.id}"
    from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com'
    recipient_list = [user.email]

    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print(f"Failed to send email: {str(e)}")  # 디버깅
        raise  # 예외를 다시 발생시켜 상위 레벨에서 처리할 수 있게 함


def perform_create(self, serializer):
    user = serializer.save()
    user.set_password(serializer.validated_data['password'])
    user.save()
    send_verification_email(user)
    return user


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data["access"]
            refresh_token = response.data["refresh"]
            response.set_cookie(
                settings.SIMPLE_JWT_AUTH_COOKIE,
                access_token,
                max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                httponly=settings.SIMPLE_JWT_AUTH_COOKIE_HTTP_ONLY,
                secure=settings.SIMPLE_JWT_AUTH_COOKIE_SECURE,
                samesite=settings.SIMPLE_JWT_AUTH_COOKIE_SAMESITE,
                path=settings.SIMPLE_JWT_AUTH_COOKIE_PATH,
            )
            response.set_cookie(
                "refresh_token",
                refresh_token,
                max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
                httponly=True,
                secure=settings.SIMPLE_JWT_AUTH_COOKIE_SECURE,
                samesite=settings.SIMPLE_JWT_AUTH_COOKIE_SAMESITE,
                path=settings.SIMPLE_JWT_AUTH_COOKIE_PATH,
            )
        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        try:
            token = RefreshToken(refresh_token)

            # 토큰이 블랙리스트에 있는지 확인
            jti = token.payload["jti"]
            if BlacklistedToken.objects.filter(token__jti=jti).exists():
                return Response(
                    {"detail": "Token is blacklisted."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                access_token = response.data["access"]
                response.set_cookie(
                    settings.SIMPLE_JWT_AUTH_COOKIE,
                    access_token,
                    max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                    httponly=settings.SIMPLE_JWT_AUTH_COOKIE_HTTP_ONLY,
                    secure=settings.SIMPLE_JWT_AUTH_COOKIE_SECURE,
                    samesite=settings.SIMPLE_JWT_AUTH_COOKIE_SAMESITE,
                    path=settings.SIMPLE_JWT_AUTH_COOKIE_PATH,
                )
            return response
        except TokenError:
            return Response(
                {"detail": "Token is invalid or expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass  # 토큰이 유효하지 않더라도 로그아웃 처리

        response = Response(
            {"detail": "Successfully logged out."}, status=status.HTTP_200_OK
        )
        response.delete_cookie(settings.SIMPLE_JWT_AUTH_COOKIE)
        response.delete_cookie("refresh_token")
        return response
