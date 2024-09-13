from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

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

    # def test_signup
