import django_filters

from credit_project.loans.models import Borrower


class BorrowerFilterSet(django_filters.rest_framework.FilterSet):
    score = django_filters.RangeFilter()

    class Meta:
        model = Borrower
        fields = ('score', )
