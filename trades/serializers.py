from rest_framework import serializers
from .models import TradeTransaction

class TradeTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeTransaction
        fields = '__all__'
        read_only_fields = ('balance_qty', 'date')
