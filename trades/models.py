
from django.db import models
from users.models import User

class TradeTransaction(models.Model):
    TRADE_TYPE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('SPLIT', 'Split'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=50)
    trade_type = models.CharField(max_length=5, choices=TRADE_TYPE_CHOICES)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Null for SPLIT
    date = models.DateTimeField(auto_now_add=True)
    balance_qty = models.PositiveIntegerField(default=0)
    split_ratio = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.trade_type} - {self.company} - {self.quantity}"
