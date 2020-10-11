# stock-trading-coding-test

A simple trading system implemented as a pure REST API (using Django) with the following endpoints:

1.) /trade = API endpoint to let users place trades. Parameters required: quantity, stock and trade_method (choice of "Buy" or "Sell")

2.) /user-trade-portfolio/<stock_name> = API endpoint to retrieve the total value invested in a single stock by a user. URL parameter required: stock_name

3.) /user-trade-portfolio = API endpoint to retrieve the total value invested by a user on all of the stocks they have traded

