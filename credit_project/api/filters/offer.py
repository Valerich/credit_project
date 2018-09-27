import django_filters

from credit_project.loans.models import Offer


class OfferFilterSet(django_filters.rest_framework.FilterSet):
    score = django_filters.NumberFilter(label='Скоринговый балл', method='filter_score')

    class Meta:
        model = Offer
        fields = ('score', 'kind', 'company')

    def filter_score(self, queryset, name, value):
        if value:
            queryset = queryset.filter(min_score__lte=value, max_score__gte=value)
        return queryset
