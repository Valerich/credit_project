from rest_framework import serializers

from credit_project.loans.models import Offer


class OfferSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:offer-detail')
    company_url = serializers.HyperlinkedIdentityField(view_name='api:company-detail',
                                                       lookup_field='company_id',
                                                       lookup_url_kwarg='pk',)

    class Meta:
        model = Offer
        fields = ('id',
                  'url',
                  'name',
                  'company',
                  'company_url',
                  'rotation_start',
                  'rotation_end',
                  'kind',
                  'min_score',
                  'max_score', )
        read_only_fields = ('created', )
