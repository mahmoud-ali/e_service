from django.urls import path, reverse_lazy

from allauth.account.views import LoginView, LogoutView, PasswordChangeView

from prices.views import (
    PriceEntryView,
    PriceReportView,
    PriceHistoryView,
    PriceComparisonView,
    FetchGoldPriceView,
)

app_name = 'prices'

urlpatterns = [
    path('', PriceEntryView.as_view(), name='entry'),
    path('report/', PriceReportView.as_view(), name='report'),
    path('history/', PriceHistoryView.as_view(), name='history'),
    path('comparison/', PriceComparisonView.as_view(), name='comparison'),
    path('fetch-gold-price/', FetchGoldPriceView.as_view(), name='fetch_gold_price'),

    # Auth pages with prices layout
    path('login/', LoginView.as_view(
        template_name='prices/login.html',
    ), name='login'),
    path('logout/', LogoutView.as_view(
        template_name='prices/logout.html',
    ), name='logout'),
    path('password/change/', PasswordChangeView.as_view(
        template_name='prices/password_change.html',
        success_url=reverse_lazy('prices:password_change'),
    ), name='password_change'),
]
