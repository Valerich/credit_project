from django import forms

from .models import Offer, Company


class OfferAdminForm(forms.ModelForm):

    class Meta:
        model = Offer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        company_qs = self.fields['company'].queryset
        company_qs = company_qs.filter(kind=Company.KIND.credit_organization)
        self.fields['company'].queryset = company_qs
