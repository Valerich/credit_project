from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

from .forms import OfferAdminForm
from .models import (
    Company,
    Borrower,
    CreditRequest,
    Offer,
)


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'kind',
                    'user', )
    list_filter = ('kind',)
    search_fields = ('name', )
    fields = ('id',
              'name',
              'kind',
              'user', )
    readonly_fields = ('id', )
    raw_id_fields = ('user', )
    list_select_related = ('user', )


class BorrowerAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'last_name',
                    'first_name',
                    'middle_name',
                    'company',
                    'created',
                    'modified', )
    list_filter = ('company', )
    search_fields = ('last_name',
                     'first_name',
                     'middle_name',
                     'phone_number',
                     '=passport_number', )
    fields = ('id',
              'last_name',
              'first_name',
              'middle_name',
              'birth_date',
              'phone_number',
              'passport_number',
              'score',
              'company',
              'created',
              'modified', )
    readonly_fields = ('id', 'created', 'modified', )
    raw_id_fields = ('company', )
    list_select_related = ('company', )


class CreditRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'borrower', 'offer', 'created', 'sent_date')
    list_filter = ('status', 'borrower', 'offer')
    search_fields = ('borrower__last_name', 'borrower__first_name', 'borrower__middle_name')
    fields = ('id', 'status', 'created', 'sent_date', 'borrower', 'offer')
    readonly_fields = ('id', 'created')
    raw_id_fields = ('borrower', 'offer')
    list_select_related = ('borrower', 'offer')


class OfferActiveListFilter(SimpleListFilter):
    title = _('Активное')
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Да')),
            ('0', _('Нет')),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            queryset = queryset.active()
        if self.value() == '0':
            queryset = queryset.not_active()
        return queryset


class OfferAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'name',
                    'company',
                    'kind',
                    'rotation_start',
                    'rotation_end',
                    'created',
                    'modified', )
    list_filter = ('kind', OfferActiveListFilter)
    search_fields = ('name', )
    fields = ('id',
              'rotation_start',
              'rotation_end',
              'name',
              'kind',
              'min_score',
              'max_score',
              'company',
              'created',
              'modified', )
    readonly_fields = ('id', 'created', 'modified')
    raw_id_fields = ('company', )
    list_select_related = ('company', )
    form = OfferAdminForm


for model_or_iterable, admin_class in (
    (Company, CompanyAdmin),
    (Borrower, BorrowerAdmin),
    (CreditRequest, CreditRequestAdmin),
    (Offer, OfferAdmin),
):
    admin.site.register(model_or_iterable, admin_class)
