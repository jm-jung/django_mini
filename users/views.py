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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        #
        # # refresh = RefreshToken.for_user(serializer.instance)
        # # response_data = {'refresh': str(refresh), 'access': str(refresh.access_token)}
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            # 이메일 인증 로직 (예시)
            # send_verification_email(user)

            # 민감한 정보를 제외한 응답 데이터
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_verification_email(user):
    # 이메일 인증 로직 구현
    subject = "Verify your email"
    message = f"Please click the link to verify your email: {settings.SITE_URL}/verify/{user.id}/"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def perform_create(self, serializer):
    user = serializer.save()
    user.set_password(serializer.validated_data["password"])
    user.save()


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
