from django.urls import path

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
]
