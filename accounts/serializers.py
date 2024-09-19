from rest_framework import serializers
from accounts.models import AccountModel
from transactions.models import Transaction

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountModel
        fields = ['account_number', 'bank_code', 'account_type', 'balance']
        read_only_fields = ['id', 'balance']

class DepositWithdrawSerializer(serializers.Serializer):
    account_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = serializers.ChoiceField(choices=Transaction.TRANSACTION_TYPES)

    def validate(self, data):
        try:
            account = AccountModel.objects.get(account_number=data['account_number'], user=self.context['request'].user)
        except AccountModel.DoesNotExist:
            raise serializers.ValidationError('계좌가 존재하지 않습니다.')

        if data['transaction_type'] == Transaction.WITHDRAWAL and account.balance < data['amount']:
            raise serializers.ValidationError('잔액이 부족하여 출금할 수 없습니다.')

        data['account'] = account
        return data