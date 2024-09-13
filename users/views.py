from django.db import transaction
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from tutorial.quickstart.serializers import UserSerializer


class RegisterView(APIView):
    class RegisterView(APIView):
        permission_classes = (AllowAny,)

        @transaction.atomic
        def post(self, request):
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    user = serializer.save()
                    if user is None:
                        return Response({"error": "User creation failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'user': serializer.data,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        from django.contrib.auth import authenticate
        user = authenticate(email=email, password=password)
        #유저가 등록한 정보와 일치하는지 확인
        if user:
            #유저가 맞으면 토큰을 줌
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.token),
            },
                status=status.HTTP_200_OK)
        return Response({'errpr': "이메일 혹은 비밀번호르 다시 확인해주세요."},
                        status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"success": "Successfully logged out."})
        except Exception as e:
            return Response({"error": str(e)}, status=400)
