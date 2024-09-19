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

    def post(self, request, *args, **kwargs):
        serializer = DepositWithdrawSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            account = serializer.validated_data['account']
            amount = serializer.validated_data['amount']
            transaction_type = serializer.validated_data['transaction_type']

            if transaction_type == Transaction.DEPOSIT:
                account.balance += amount
                transaction_description = '입금'
            else:  # WITHDRAWAL
                account.balance -= amount
                transaction_description = '출금'

            # 계좌 잔액을 업데이트하여 저장
            account.save()

            # 거래 기록을 생성하고 저장
            transaction = Transaction.objects.create(
                account_info=account,
                transaction_amount=amount,
                balance_after_transaction=account.balance,
                transaction_description=transaction_description,
                transaction_type=transaction_type,
                transaction_method='Manual' # 필요에 따라 수정할 수 있음
            )

            # 거래 데이터를 직렬화
            transaction_serializer = TransactionSerializer(transaction)

            # 성공 응답을 반환
            return Response(transaction_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




