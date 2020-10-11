from django.contrib import admin

from codingtest.stocktrading import models


admin.site.register(models.Stock)
admin.site.register(models.UserStockTradeOrder)
