from django.urls import path
from .views import RecordTradeView, StockSummaryView

urlpatterns = [
    path('record/<str:trade_type>/', RecordTradeView.as_view(), name='record_trade'),
    path('summary/', StockSummaryView.as_view(), name='stock_summary'),

]
