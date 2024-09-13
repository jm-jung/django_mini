from django.db import IntegrityError
from django.test import TestCase

from accounts.models import AccountModel
from users.models import Users


class AccountsTestCase(TestCase):

    def setUp(self) -> None:

        self.user = Users.objects.create_user(
            email="testuser@example.com",
            password="testpass",
            phone_number="01012345678",
        )

        self.account = AccountModel.objects.create(
            user=self.user,
            account_number="1234567890",
            bank_code="kakao",
            account_type="savings",
            balance=1000.00,
        )

    def test_account_creation(self) -> None:

        account = AccountModel.objects.get(account_number="1234567890")
        self.assertEqual(account.user, self.user)
        self.assertEqual(account.bank_code, "kakao")
        self.assertEqual(account.account_type, "savings")
        self.assertEqual(account.balance, 1000.00)

    def test_unique_constraints(self) -> None:

        with self.assertRaises(IntegrityError):
            AccountModel.objects.create(
                user=self.user,
                account_number="1234567890",
                bank_code="kb",
                account_type="checking",
                balance=500.00,
            )
