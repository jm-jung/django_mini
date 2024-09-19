from django.db import transaction
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from accounts.serializers import AccountSerializer
from accounts.models import AccountModel
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer
from .serializers import DepositWithdrawSerializer

class AccountQuerySetMixin:
    queryset = AccountModel.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]



# 계좌 생성 및 조회
class AccountListCreateView(AccountQuerySetMixin, ListCreateAPIView):
    def perform_create(self, serializer): # 로그인한 사용자를 해당 계좌의 소유자로 설정합니다.

        account_number = serializer.validated_data['account_number']
        if AccountModel.objects.filter(account_number=account_number).exists():
            raise ValidationError('이미 존재하는 계좌번호입니다.')
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs): # 계좌 생성

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 특정 계좌 조회 및 삭제
class AccountDetailView(AccountQuerySetMixin, RetrieveDestroyAPIView):
    def perform_destroy(self, instance):

        if instance.balance > 0:
            raise ValidationError('계좌에 잔액이 남아있으면 삭제할 수 없습니다.')
        instance.delete()


class DepositWithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = DepositWithdrawSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            source_account = serializer.validated_data['account']
            amount = serializer.validated_data['amount']
            transaction_type = serializer.validated_data['transaction_type']

            target_account_number = request.data.get('target_account_number')
            target_account = None
            if target_account_number:
                try:
                    target_account = AccountModel.objects.get(account_number=target_account_number)
                except AccountModel.DoesNotExist:
                    raise ValidationError('송금 대상 계좌가 존재하지 않습니다.')

            if transaction_type == Transaction.WITHDRAWAL:
                if source_account.balance < amount:
                    raise ValidationError('잔액이 부족하여 출금할 수 없습니다.')
                source_account.balance -= amount
                if target_account:
                    target_account.balance += amount
                    transaction_description = '출금 및 입금'
                else:
                    transaction_description = '출금'

            elif transaction_type == Transaction.DEPOSIT:
                source_account.balance += amount
                transaction_description = '입금'

            source_account.save()
            if target_account:
                target_account.save()

            transaction = Transaction.objects.create(
                account_info=source_account,
                transaction_amount=amount,
                balance_after_transaction=source_account.balance,
                transaction_description=transaction_description,
                transaction_type=transaction_type,
                transaction_method='Manual'
            )

            transaction_serializer = TransactionSerializer(transaction)
            return Response(transaction_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




