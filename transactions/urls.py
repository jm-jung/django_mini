from django.urls import path

from accounts.views import DepositWithdrawView
from .views import TransactionDetailView, TransactionListCreateView

urlpatterns = [
    path('deposit-withdraw/', DepositWithdrawView.as_view(), name='deposit-withdraw'),
    path("", TransactionListCreateView.as_view(), name="transaction_list_create"),
    path("<int:pk>/", TransactionDetailView.as_view(), name="transaction_detail"),
]
