from rest_framework import serializers

from codingtest.stocktrading.models import Stock
from codingtest.stocktrading.models import UserStockTradeOrder


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('name', 'price',)


class UserStockTradeSerializer(serializers.ModelSerializer):
    stock = serializers.PrimaryKeyRelatedField(
        queryset=Stock.objects.all(),
        required=True
    )
    quantity = serializers.IntegerField(required=True)
    trade_method = serializers.ChoiceField(
        choices=UserStockTradeOrder.TRADE_CHOICES,
        required=True
    )

    class Meta:
        model = UserStockTradeOrder
        fields = ('stock', 'quantity', 'trade_method',)


class UserInvestedForStockSerializer(serializers.ModelSerializer):
    stock = serializers.CharField(required=True)

    class Meta:
        model = UserStockTradeOrder
        fields = ('stock',)
