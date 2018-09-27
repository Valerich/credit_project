from rest_framework import serializers

from credit_project.loans.models import Company


class CompanySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:company-detail')

    class Meta:
        model = Company
        fields = (
            'id',
            'url',
            'name',
        )
