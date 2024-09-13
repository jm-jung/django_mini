from rest_framework.serializers import ModelSerializer

from transactions.models import Transaction


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"

    def get_masked_account_number(self, objects):
        account_number = objects.account_info.account_number
        if not account_number:
            return None

        masked_account_number = account_number[:-4] + "*" * (
            len(account_number) - (len(account_number) - 4)
        )
        return masked_account_number

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["masked_account_number"] = self.get_masked_account_number(
            instance
        )
        return representation
