from django.db import models
from django.utils import timezone

from accounts.models import Account


class Transaction(models.Model):
    DEPOSIT = 'DE'
    WITHDRAWAL = 'WI'
    TRANSACTION_TYPES = [
        (DEPOSIT, 'Deposit'),
        (WITHDRAWAL, 'Withdrawal'),
    ]

    account_info = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_amount = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after_transaction = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_description = models.CharField(max_length=20)
    transaction_type = models.CharField(
        max_length=2,
        choices=TRANSACTION_TYPES,
        default=DEPOSIT,
    )
    transaction_method = models.CharField(max_length=20)  # Assuming this field is for deposit/withdrawal method
    transaction_datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_amount}"
