from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import Users

User = get_user_model()


class UsersTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            "name": "test",
            "email": "example@example.com",
            "password": "1234",
            "nickname": "test_test",
            "phone_number": "1234567890",
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.name, "test")

    def test_str_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data["nickname"])

    def test_email_create(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, "example@example.com")

    def test_email_unique(self):
        User.objects.create_user(**self.user_data)
        self.assertRaises(IntegrityError, User.objects.create_user, **self.user_data)

    def test_email_Not_null(self):
        data = self.user_data
        # data['email'] = ''
        data.pop("email")
        with self.assertRaises(IntegrityError):
            User.objects.create(email=None, **data)

    def test_nickname_Not_null(self):
        data = self.user_data
        data.pop("nickname")
        with self.assertRaises(IntegrityError):
            User.objects.create(nickname=None, **data)

    def test_Phone_number_Not_null(self):
        data = self.user_data
        data.pop("phone_number")
        with self.assertRaises(IntegrityError):
            User.objects.create(phone_number=None, **data)

    def test_password_Not_null(self):
        data = self.user_data
        data.pop("password")
        with self.assertRaises(IntegrityError):
            User.objects.create(password=None, **data)

    def test_Is_active_default(self):
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(user.is_active)

    def test_Is_staff_default(self):
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_staff)

    def test_is_admin_default(self):
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_admin)


class UserSignUpTestCase(TestCase):
    url = reverse("register")

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("register")
        self.login_url = reverse("token_obtain_pair")
        self.logout_url = reverse("logout")
        self.user_data = {
            "name": "test",
            "email": "example@example.com",
            "password": "12345678",
            "password2": "12345678",
            "nickname": "test_test",
            "phone_number": "1234567890",
        }

    def test_create_user(self):
        user_data = self.user_data.copy()
        user_data["password"] = "TestPassword123!"
        user_data["password2"] = "TestPassword123!"
        response = self.client.post(self.register_url, user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, user_data["email"])

    def test_create_user_already_exists(self):
        self.client.post(self.register_url, self.user_data, format="json")
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_match_password(self):
        user = self.user_data
        self.assertEqual(user["password"], user["password2"])

    def test_already_email(self):
        # 첫 번째 사용자 생성
        user_data = self.user_data.copy()
        user_data["password"] = "TestPassword123!"
        user_data["password2"] = "TestPassword123!"
        response = self.client.post(self.register_url, user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        # 같은 이메일로 두 번째 사용자 생성 시도
        new_user_data = user_data.copy()
        new_user_data["nickname"] = "new_nickname"
        new_user_data["password"] = "TestPassword123!"
        new_user_data["password2"] = "TestPassword123!"
        response = self.client.post(self.register_url, new_user_data, format="json")

        # 응답 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)  # 이메일 관련 오류 메시지 확인
        self.assertIn(
            "already exists", str(response.data["email"]).lower()
        )  # 'already exists' 문구 확인

        # 사용자 수가 여전히 1명인지 확인
        self.assertEqual(User.objects.count(), 1)

    def test_invalid_email(self):
        invalid_email_data = self.user_data.copy()
        invalid_email_data["email"] = "invalid-email"
        response = self.client.post(
            self.register_url, invalid_email_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_password_too_short(self):
        short_password_data = self.user_data.copy()
        short_password_data["password"] = "1234"
        short_password_data["password2"] = "1234"
        response = self.client.post(
            self.register_url, short_password_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This password is too short", str(response.data))

    def test_password_hashing(self):
        user_data = self.user_data.copy()
        user_data["password"] = "TestPassword123!"
        user_data["password2"] = "TestPassword123!"
        response = self.client.post(self.register_url, user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.user_data["email"])
        self.assertNotEqual(self.user_data["password"], user.password)

    # def test_email_verification(self):
    #     response = self.client.post(self.register_url, self.user_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(len(mail.outbox), 1)
    #     self.assertIn('Verify your email', mail.outbox[0].subject)

    def test_jwt_login(self):
        # 사용자 생성 및 이메일 인증 (이 부분은 귀하의 인증 로직에 맞게 조정해야 합니다)
        user_data = self.user_data.copy()
        user_data.pop("password2")
        user = User.objects.create_user(**user_data)
        user.is_active = True
        user.save()

        response = self.client.post(
            self.login_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_jwt_logout(self):
        # 사용자 생성 및 로그인
        user_data = self.user_data.copy()
        user_data.pop("password2")
        user = User.objects.create_user(**user_data)
        user.is_active = True
        user.save()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # 액세스 토큰으로 인증
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # 로그아웃
        response = self.client.post(
            self.logout_url, {"refresh": str(refresh)}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": "Successfully logged out."})

        # 쿠키가 '삭제'되었는지 확인 (값이 비어있고 만료되었는지)
        self.assertIn(settings.SIMPLE_JWT_AUTH_COOKIE, response.cookies)
        self.assertEqual(response.cookies[settings.SIMPLE_JWT_AUTH_COOKIE].value, "")
        self.assertTrue(
            response.cookies[settings.SIMPLE_JWT_AUTH_COOKIE]["expires"].startswith(
                "Thu, 01 Jan 1970"
            )
        )

        self.assertIn("refresh_token", response.cookies)
        self.assertEqual(response.cookies["refresh_token"].value, "")
        self.assertTrue(
            response.cookies["refresh_token"]["expires"].startswith("Thu, 01 Jan 1970")
        )

        # 로그아웃 후 보호된 뷰에 접근 시도 (예시)
        # 실제 보호된 뷰의 URL로 변경해야 합니다
        protected_url = reverse(
            "logout"
        )  # 'some-protected-view'를 실제 뷰 이름으로 변경
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # 토큰 갱신 시도
        refresh_url = reverse(
            "token_refresh"
        )  # 'token_refresh'를 실제 토큰 갱신 URL 이름으로 변경
        response = self.client.post(
            refresh_url, {"refresh": str(refresh)}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
