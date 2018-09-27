from django.conf.urls import include, url

from rest_framework import routers

from .views import (
    BorrowerViewSet,
    CompanyViewSet,
    CreditRequestViewSet,
    OfferViewSet,
)


router = routers.DefaultRouter()
router.register(r'borrowers', BorrowerViewSet, base_name='borrower')
router.register(r'companies', CompanyViewSet, base_name='company')
router.register(r'credit-requests', CreditRequestViewSet, base_name='credit_request')
router.register(r'offers', OfferViewSet, base_name='offer')


urlpatterns = [
    url(r'^$', router.get_api_root_view()),
    url(r'^', include(router.urls)),
]
