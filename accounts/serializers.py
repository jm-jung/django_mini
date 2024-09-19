from rest_framework import serializers

from accounts.models import AccountModel


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountModel
        fields = ["account_number", "bank_code", "account_type", "balance"]
        read_only_fields = ["id", "balance"]
