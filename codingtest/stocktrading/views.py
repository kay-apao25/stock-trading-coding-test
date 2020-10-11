from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from codingtest.stocktrading.models import Stock
from codingtest.stocktrading.models import UserStockTradeOrder

from codingtest.stocktrading.serializers import UserStockTradeSerializer
from codingtest.stocktrading.serializers import UserInvestedForStockSerializer


class UserTradeView(APIView):
    """
    API endpoint that allows users to place trades.
    """
    serializer_class = UserStockTradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UserStockTradeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stock = serializer.data['stock']
        trade_method = serializer.data['trade_method']
        stock_quantity = serializer.data['quantity']

        user = get_object_or_404(User, username=request.user.username)
        stock = get_object_or_404(Stock, pk=stock)
        stock_quantity = int(stock_quantity)

        user_stock = UserStockTradeOrder.objects.create(
            user=user,
            stock=stock,
            trade_method=trade_method
        )

        on_hand_stocks = user_stock.get_total_value_invested_per_stock(
            user=request.user,
            for_stock=stock,
        )

        if trade_method == 'Buy':
            if stock_quantity <= 0:
                return Response(
                    {"message": "Quantity value must be greater than 0"},
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )
            user_stock.quantity = stock_quantity
            on_hand_stocks += stock_quantity
        elif trade_method == 'Sell':
            if stock_quantity > on_hand_stocks:
                msg = "Stock quantity to sell more " \
                    "than stock quantity on-hand. Stock " \
                    "available on-hand: {}"
                return Response(
                    {"message": msg.format(on_hand_stocks)},
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )
            user_stock.quantity = stock_quantity * (-1)
            on_hand_stocks -= stock_quantity
        else:
            return Response(
                {"message": "Invalid trade method"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_stock.save()
        msg = 'Stock trade {} processing was successful'
        return Response(
            {
                "message": msg.format(trade_method),
            },
            status.HTTP_200_OK
        )


class UserInvestedForStockView(APIView):
    """
    API endpoint to retrieve the total value
    invested in a single stock or for all stocks
    by a user
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, stock=None):
        if stock:
            serializer = UserInvestedForStockSerializer(
                data={'stock': stock}
            )
            serializer.is_valid(raise_exception=True)

            stock_name = serializer.data['stock']
            stock = get_object_or_404(Stock, name=stock_name)

        total = UserStockTradeOrder.get_total_value_invested_per_stock(
            user=request.user,
            for_stock=stock
        )

        msg = 'Total value invested for stock {} is {}'
        if isinstance(total, int):
            return Response(
                {
                    "message": msg.format(stock_name, (total*stock.price))
                },
                status.HTTP_200_OK
            )

        result = {}
        for stock in total:
            stock_obj = get_object_or_404(Stock, pk=stock['stock'])
            result[stock_obj.name] = (
                msg.format(stock_obj.name, (stock['total'] * stock_obj.price))
            )

        return Response(
            result,
            status.HTTP_200_OK
        )
