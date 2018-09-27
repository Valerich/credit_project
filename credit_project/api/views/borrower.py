from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from credit_project.loans.models import Borrower
from ..filters import BorrowerFilterSet
from ..permissions import (
    ListForPartnerOrSuperUser,
    DetailForOwnerOrSuperUser,
    EditForSuperUser,
    DeleteForSuperUser,
    CreateForPartnerOrSuperUser,
)
from ..serializers import BorrowerSerializer


class BorrowerViewSet(ModelViewSet):
    permission_classes = [ListForPartnerOrSuperUser,
                          DetailForOwnerOrSuperUser,
                          CreateForPartnerOrSuperUser,
                          EditForSuperUser,
                          DeleteForSuperUser, ]
    serializer_class = BorrowerSerializer

    search_fields = ('last_name',
                     'first_name',
                     'middle_name',
                     'phone_number',
                     'passport_number', )
    filter_class = BorrowerFilterSet

    def get_queryset(self):
        queryset = Borrower.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                company=self.request.user.company)
        return queryset
