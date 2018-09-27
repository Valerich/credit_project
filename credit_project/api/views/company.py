from rest_framework.viewsets import ReadOnlyModelViewSet

from credit_project.loans.models import Company
from ..permissions import ListForCompanyOrSuperUser, DetailForOwnerOrSuperUser
from ..serializers import CompanySerializer


class CompanyViewSet(ReadOnlyModelViewSet):
    permission_classes = (ListForCompanyOrSuperUser,
                          DetailForOwnerOrSuperUser, )
    serializer_class = CompanySerializer

    def get_queryset(self):
        qs = Company.objects.all()
        if not self.request.user.is_superuser:
            qs = qs.filter(id=self.request.user.company.id)
        return qs
