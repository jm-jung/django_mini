from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import AccountModel
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer

User = get_user_model()


class TransactionSerializerTests(TestCase):
    def setUp(self) -> None:
        # 테스트 유저 생성
        self.user = User.objects.create_user(
            name="test",
            email="example@example.com",
            password="1234",
            nickname="test_test",
            phone_number="1234567890",
        )
        # 테스트 계좌 생성
        self.account = AccountModel.objects.create(
            account_number="123412341234",
            balance=1000,
            user=self.user,
        )
        # 테스트 거래 내역 생성
        self.transaction = Transaction.objects.create(
            account_info=self.account,
            transaction_amount=100,
            balance_after_transaction=1100,
            transaction_description="TEST",
            transaction_type=Transaction.DEPOSIT,
            transaction_method="deposit",
        )

        self.serializer = TransactionSerializer(self.transaction)

    def test_masked_account_number(self) -> None:
        data = self.serializer.data
        masked_account_number = data["masked_account_number"]

        expedted_masked_account_number = "12341234****"
        self.assertEqual(masked_account_number, expedted_masked_account_number)

    def test_transaction_serializer(self) -> None:
        data = self.serializer.data
        self.assertEqual(data["transaction_amount"], "100.00")
        self.assertEqual(data["balance_after_transaction"], "1100.00")
        self.assertEqual(data["transaction_description"], "TEST")
        self.assertEqual(data["transaction_type"], "DE")
        self.assertEqual(data["transaction_method"], "deposit")
        self.assertEqual(data["masked_account_number"], "12341234****")

    def test_api_response(self) -> None:
        client = APIClient()
        response = client.get("/transactions/{}/".format(self.transaction.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertIn("masked_account_number", response_data)
        self.assertEqual(response_data["masked_account_number"], "12341234****")
