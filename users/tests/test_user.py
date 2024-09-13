from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
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
    url = reverse("user-register")

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-register')
        self.user_data = {
            "email": "example@example.com",
            "password": "12345678",
            "password2": "12345678",
            "nickname": "test_test",
            "phone_number": "1234567890",
        }

    def test_create_user(self):
        user = self.user_data
        response = self.client.post(self.register_url, user, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, user["email"])

    def test_create_user_already_exists(self):
        user = self.user_data
        response = self.client.post(self.register_url, user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_match_password(self):
        user = self.user_data
        self.assertEqual(user["password"], user["password2"])

    def test_already_email(self):
        user = self.user_data
        response = self.client.post(self.register_url, user, format='json')
        new_user = user.copy()
        new_user['email'] = user["email"]
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_invalid_email(self):
        user = self.user_data
        response = self.client.post(self.register_url, user, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        short_password_data = self.user_data.copy()  # 원본 데이터를 변경하지 않기 위해 복사
        short_password_data["password"] = "1234"
        short_password_data["password2"] = "1234"
        response = self.client.post(self.register_url, short_password_data, format='json')
        self.assertEqual(response.status_code, 405)
        self.assertIn('password', response.data)

    def test_password_hashing(self):
        user = self.user_data
        response = self.client.post(self.register_url, user, format='json')
        self.assertNotEqual(response["password"], user["password"])
