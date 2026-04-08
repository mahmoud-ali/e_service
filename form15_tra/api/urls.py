from django.urls import path, include
from rest_framework.routers import DefaultRouter
from form15_tra.api.views import CollectionFormViewSet, MarketViewSet

router = DefaultRouter()
router.register(r'collections', CollectionFormViewSet, basename='collection')
router.register(r'markets', MarketViewSet, basename='market')

urlpatterns = [
    path('', include(router.urls)),
]
