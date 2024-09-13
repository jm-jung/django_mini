from rest_framework import serializers

from accounts.models import AccountModel
from transactions.models import Transaction


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountModel
        fields = '__all__'
        read_only_fields = ['id','balance']



class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['id', 'balance_after_transaction', 'transaction_datetime']
