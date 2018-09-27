from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LoansConfig(AppConfig):
    name = 'credit_project.loans'
    verbose_name = _("Кредитование")
