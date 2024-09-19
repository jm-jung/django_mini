from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import Users

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["email", "password", "password2", "phone_number", "name", "nickname"]
        extra_kwargs = {
            "email": {"required": True},
            # 'password': {'write_only': True},
            "phone_number": {"required": True},
            "name": {"required": True},
            "nickname": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        try:
            validate_password(attrs["password"])
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        attrs.pop("password2", None)
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password2", None)  # password2 필드 제거
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    pass


class NicknameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['nickname']

    def create(self, validated_data):
        user = Users(**validated_data)
        user.set_password(Users.objects.make_random_password())
        user.save()
        return user
