from django.test import TestCase
from .models import Account, Transaction
from django.utils import timezone


class TransactionModelTest(TestCase):

    def setUp(self):
        now = timezone.now()
        # 테스트 계좌를 생성합니다.
        self.account = Account.objects.create(account_number='1234567890', balance=1000.00)
        # 테스트 트랜잭션을 생성합니다.
        self.transaction = Transaction.objects.create(
            account_info=self.account,
            transaction_amount=100.00,
            balance_after_transaction=900.00,
            transaction_description='Test transaction',
            transaction_type=Transaction.DEPOSIT,
            transaction_method='Online',
            transaction_datetime=now
        )

    def test_transaction_creation(self):
        transaction = Transaction.objects.get(id=self.transaction.id)
        self.assertEqual(transaction.account_info, self.account)
        self.assertEqual(transaction.transaction_amount, 100.00)
        self.assertEqual(transaction.balance_after_transaction, 900.00)
        self.assertEqual(transaction.transaction_description, 'Test transaction')
        self.assertEqual(transaction.transaction_type, Transaction.DEPOSIT)
        self.assertEqual(transaction.transaction_method, 'Online')

        now = timezone.now().replace(microsecond=0)
        transaction_datetime = transaction.transaction_datetime.replace(microsecond=0)
        self.assertEqual(transaction_datetime, now)
