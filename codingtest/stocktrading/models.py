from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User


class Stock(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(
        default=Decimal('0.00'),
        max_digits=5,
        decimal_places=2
    )

    def __str__(self):
        return '%s' % self.name


class UserStockTradeOrder(models.Model):
    TRADE_CHOICES = (
        ('Buy', 'Buy'),
        ('Sell', 'Sell'),
    )

    user = models.ForeignKey(
        User,
        related_name='user_stock',
        on_delete=models.DO_NOTHING
    )
    stock = models.ForeignKey(
        'Stock',
        related_name='stock_user_invested',
        on_delete=models.DO_NOTHING
    )
    trade_method = models.CharField(choices=TRADE_CHOICES, max_length=10)
    quantity = models.IntegerField(default=0)

    @classmethod
    def get_total_value_invested_per_stock(cls, user, for_stock):
        user_orders = cls.objects.filter(user=user)
        if for_stock:
            user_stock_orders = user_orders.filter(stock=for_stock)
            return user_stock_orders.aggregate(
                total=models.Sum('quantity')
            ).get('total')
        else:
            user_stock_orders = user_orders
            return user_stock_orders.values('stock') \
                                    .order_by('stock') \
                                    .annotate(total=models.Sum('quantity'))
