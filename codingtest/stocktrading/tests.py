import random

from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from codingtest.stocktrading.models import Stock
from codingtest.stocktrading.models import UserStockTradeOrder


class TradeTestCase(APITestCase):
    def setUp(self):
        self.username = 'cypress'
        self.password = 'w@ndEr'
        self.user = User.objects.create(
            username=self.username,
            password=self.password
        )
        self.client.force_authenticate(user=self.user)
        self.stock = Stock.objects.create(
            name='Stock1',
            price=1.00
        )
        self.data = {
            'stock': self.stock.id,
            'quantity': 1,
            'trade_method': 'Buy'
        }

    def test_trade_sunny_scenario(self):
        response = self.client.post(
            '/trade',
            self.data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)

    def test_trade_sunny_scenario_check_trade_messages(self):
        # Buy trade method
        response = self.client.post(
            '/trade',
            self.data,
            format='json'
        )
        self.assertTrue(
            'Stock trade Buy' in response.json()['message']
        )

        # Sell trade method
        self.data['trade_method'] = 'Sell'
        response = self.client.post(
            '/trade',
            self.data,
            format='json'
        )
        self.assertTrue(
            'Stock trade Sell' in response.json()['message']
        )

    def test_trade_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            '/trade',
            self.data,
            format='json'
        )
        self.assertEqual(response.status_code, 403)

    def test_trade_get_method(self):
        response = self.client.get(
            '/trade',
            self.data,
            format='json'
        )
        self.assertEqual(response.status_code, 405)

    def test_trade_inexistent_stock(self):
        self.data['stock'] = 3
        response = self.client.post(
            '/trade',
            self.data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_trade_sell_insufficient_stock_quantity_onhand(self):
        self.client.post(
            '/trade',
            self.data,
            format='json'
        )

        self.data['trade_method'] = 'Sell'
        self.data['quantity'] = 100
        response = self.client.post(
            '/trade',
            self.data,
            format='json'
        )
        self.assertTrue(
            'Stock quantity to sell more ' +
            'than stock quantity on-hand.' in
            response.json()['message'],
        )

    def test_trade_not_supplying_all_inputs_needed(self):
        # Not providing any details
        response = self.client.post(
            '/trade',
            format='json'
        )
        self.assertEqual(response.status_code, 400)

        # Not providing stock input
        del self.data['stock']
        response = self.client.post(
            '/trade',
            self.data,
            format='json'
        )
        self.assertEqual(
            response.json()['stock'][0],
            'This field is required.'
        )

        # Not providing quantity input
        del self.data['quantity']
        response = self.client.post(
            '/trade',
            self.data,
            format='json'
        )
        self.assertEqual(
            response.json()['quantity'][0],
            'This field is required.'
        )

        # Not providing trade_method input
        del self.data['trade_method']
        response = self.client.post(
            '/trade',
            self.data,
            format='json'
        )
        self.assertEqual(
            response.json()['trade_method'][0],
            'This field is required.'
        )

    def test_trade_incorrect_inputs(self):
        # Quantity less than or equal to zero
        self.data['quantity'] = random.randint(-100, 0)
        response = self.client.post(
            '/trade',
            self.data,
            format='json'
        )
        self.assertEqual(
            response.json()['message'],
            'Quantity value must be greater than 0'
        )

        # Quantity value an empty string
        self.data['quantity'] = ''
        response = self.client.post(
            '/trade',
            self.data,
            format='json'
        )
        self.assertEqual(
            response.json()['quantity'][0],
            'A valid integer is required.'
        )

        # Incorrect trade_method input
        self.data['trade_method'] = 'Order'
        response = self.client.post(
            '/trade',
            self.data,
            format='json'
        )
        self.assertEqual(
            response.json()['trade_method'][0],
            '"Order" is not a valid choice.'
        )

        # Stock value an empty string
        self.data['stock'] = ''
        response = self.client.post(
            '/trade',
            self.data,
            format='json'
        )
        self.assertEqual(
            response.json()['stock'][0],
            'This field may not be null.'
        )


class UserStockTradePortfolopTestCase(APITestCase):
    def setUp(self):
        self.username = 'cypress'
        self.password = 'w@ndEr'
        self.user = User.objects.create(
            username=self.username,
            password=self.password
        )
        self.client.force_authenticate(user=self.user)
        self.stock = Stock.objects.create(
            name='Stock1',
            price=1.00
        )
        self.user_stock = UserStockTradeOrder.objects.create(
            user=self.user,
            stock=self.stock,
            trade_method='Buy'
        )
        self.data = {
            'stock': self.stock.name,
        }

    def test_user_trade_portfolio_sunny_scenario(self):
        # For a specific stock of a user
        response = self.client.get(
            '/user-trade-portfolio/{}'.format(self.stock.name),
            format='json'
        )
        self.assertEqual(response.status_code, 200)

        # For all stocks of a user
        response = self.client.get(
            '/user-trade-portfolio',
            format='json'
        )
        self.assertTrue(
            isinstance(response.json(), object)
        )
        self.assertTrue(
            self.stock.name in response.json()
        )
        self.assertTrue(
            'Total value invested' in
            response.json()[self.stock.name]
        )

    def test_trade_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(
            '/user-trade-portfolio',
            self.data,
            format='json'
        )
        self.assertEqual(response.status_code, 403)

    def test_trade_post_method(self):
        response = self.client.post(
            '/user-trade-portfolio',
            self.data,
            format='json'
        )
        self.assertEqual(response.status_code, 405)

    def test_user_trade_portfolio_inexistent_stock(self):
        response = self.client.get(
            '/user-trade-portfolio/St',
            format='json'
        )
        self.assertEqual(response.status_code, 404)
