from django.db import IntegrityError
from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

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

class AccountModelTests(APITestCase):
    def setUp(self):
        # 테스트용 사용자 생성
        self.user = Users.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            phone_number='1234567890'
        )
        # 테스트용 계좌 생성
        self.account = AccountModel.objects.create(
            user=self.user,
            account_number='1234567890',
            bank_code='kakao',
            account_type='checking',
            balance=1000
        )
        # API 엔드포인트 URL 설정
        self.list_create_url = reverse('account-list-create')
        self.detail_url = reverse('account-detail', args=[self.account.pk])

    def test_create_account(self):
        """
        계좌 생성 테스트
        """
        data = {
            'account_number': '0987654321',
            'bank_code': 'kb',
            'account_type': 'savings',
            'balance': 500
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AccountModel.objects.count(), 2)
        self.assertEqual(AccountModel.objects.latest('id').account_number, '0987654321')

    def test_retrieve_account(self):
        """
        계좌 조회 테스트
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['account_number'], self.account.account_number)

    def test_delete_account(self):
        """
        계좌 삭제 테스트
        """
        self.client.force_authenticate(user=self.user)

        # 계좌의 잔액을 0으로 설정
        self.account.balance = 0
        self.account.save()

        response = self.client.delete(self.detail_url, format='json')

        # 삭제가 성공해야 함
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AccountModel.objects.count(), 0)

    def test_delete_account_with_balance(self):
        """
        잔액이 남아있는 계좌 삭제 테스트
        """
        self.account.balance = 1000  # 잔액이 있는 상태로 설정
        self.account.save()
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(AccountModel.objects.count(), 1)
