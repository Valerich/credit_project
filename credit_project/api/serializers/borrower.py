from phonenumber_field.modelfields import PhoneNumberField
from rest_framework import serializers

from credit_project.loans.models import Borrower


class BorrowerSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:borrower-detail')
    phone_number = serializers.CharField(validators=PhoneNumberField().validators)
    company_url = serializers.HyperlinkedIdentityField(view_name='api:company-detail',
                                                       lookup_field='company_id',
                                                       lookup_url_kwarg='pk')

    class Meta:
        model = Borrower
        fields = ('id',
                  'url',
                  'last_name',
                  'first_name',
                  'middle_name',
                  'birth_date',
                  'phone_number',
                  'passport_number',
                  'score',
                  'company',
                  'company_url', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self.context['request'].user

        if not self.user.is_superuser:
            self.fields['company'].read_only = True


    def validate(self, attrs):
        if not self.user.is_superuser:
            attrs['company'] = self.user.company
        return attrs

