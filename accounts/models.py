from django.db import models


class AccountModel(models.Model):
    BANK_CODE_CHOICES = [
        ('kakao', '카카오뱅크'),
        ('kb', '국민은행'),
        ('nh', '농협은행'),
        ('ibk', '기업은행'),

    ]

    ACCOUNT_TYPE_CHOICES = [
        ('checking', '입출금통장'),
        ('savings', '저축통장'),

    ]
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    account_number = models.CharField("계좌번호", max_length=20, unique=True)
    bank_code = models.CharField("은행 코드", max_length=20, choices=BANK_CODE_CHOICES)
    account_type = models.CharField("계좌 종류", max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    balance = models.DecimalField("잔액", max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user} - {self.account_number} ({self.bank_code})"



