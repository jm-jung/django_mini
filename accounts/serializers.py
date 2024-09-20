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
            # 계좌번호에 해당하는 계좌를 가져옴 (소유자와 상관없이)
            account = AccountModel.objects.get(account_number=data['account_number'])
        except AccountModel.DoesNotExist:
            raise serializers.ValidationError('계좌가 존재하지 않습니다.')

        if data['transaction_type'] == Transaction.WITHDRAWAL:
            # 출금의 경우, 현재 로그인한 사용자만 자기 계좌에서 출금할 수 있도록 제한
            if account.user != self.context['request'].user:
                raise serializers.ValidationError('자신의 계좌에서만 출금할 수 있습니다.')

            if account.balance < data['amount']:
                raise serializers.ValidationError('잔액이 부족하여 출금할 수 없습니다.')

        data['account'] = account
        return data