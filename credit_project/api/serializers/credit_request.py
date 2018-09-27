from rest_framework import serializers

from credit_project.api.serializers.borrower import BorrowerSerializer
from credit_project.loans.models import CreditRequest


class CreditRequestSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api:credit_request-detail')
    borrower_detail = serializers.SerializerMethodField()
    offer_url = serializers.HyperlinkedIdentityField(view_name='api:offer-detail',
                                                     lookup_field='offer_id',
                                                     lookup_url_kwarg='pk')

    class Meta:
        model = CreditRequest
        fields = ('id',
                  'url',
                  'status',
                  'created',
                  'sent_date',
                  'borrower',
                  'borrower_detail',
                  'offer',
                  'offer_url', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self.context['request'].user

        self.fields['sent_date'].read_only = True

        if not self.instance:
            # Заявка не обязательна для добавления.
            # Если она не передана, то создаем заявки для всех подходящих предложений
            self.fields['offer'].required = False
            self.fields['offer'].allow_null = True
            # Статус можно менять только при редактировании
            self.fields['status'].read_only = True

        elif not self.user.is_superuser:
            # Не суперпользователям нельзя редактировать ничего, кроме поля status
            for field_name, field in self.fields.items():
                if field_name != 'status':
                    field.read_only = True

        if not self.user.is_superuser:
            # При создании заявки можно указать только свои анкеты
            if hasattr(self.user, 'company'):
                self.fields['borrower'].queryset = self.fields['borrower'].queryset.filter(
                    company=self.user.company)
            else:
                self.fields['borrower'].queryset = self.fields['borrower'].queryset.none()

        self.fields['offer'].queryset = self.fields['offer'].queryset.active()

    def get_borrower_detail(self, obj):
        return BorrowerSerializer(obj.borrower, context=self.context).data
