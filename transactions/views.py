from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from transactions.models import Transaction
from transactions.serializers import TransactionSerializer


class TransactionListCreateView(ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def perform_create(self, serializer):
        account_info = serializer.validate.get("account_info")
        if not account_info:
            raise ValidationError("유효하지 않은 계좌입니다.")

        serializer.save()


class TransactionDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_object(self):
        objects = super().get_object()

        return objects
