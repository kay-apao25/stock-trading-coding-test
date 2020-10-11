from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path

from codingtest.stocktrading import views


urlpatterns = [
    url(r'^trade', views.UserTradeView.as_view()),
    url(
        r'^user-trade-portfolio/(?P<stock>[^/.]+)',
        views.UserInvestedForStockView.as_view()
    ),
    # This endpoint will return all the total value invested
    # by the authenticated user by stock
    url(
        r'^user-trade-portfolio',
        views.UserInvestedForStockView.as_view()
    ),

    path('admin/', admin.site.urls),
    path(
        'api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    )
]
