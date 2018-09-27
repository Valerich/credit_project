from rest_framework.viewsets import ReadOnlyModelViewSet

from credit_project.loans.models import Offer
from ..filters import OfferFilterSet
from ..permissions import ListForPartnerOrSuperUser
from ..serializers import OfferSerializer


class OfferViewSet(ReadOnlyModelViewSet):
    permission_classes = [ListForPartnerOrSuperUser,
                          ]
    serializer_class = OfferSerializer

    search_fields = ('name', )
    filter_class = OfferFilterSet

    def get_queryset(self):
        qs = Offer.objects.all()
        if not self.request.user.is_superuser:
            qs = qs.active()
        return qs
