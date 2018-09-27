from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_passport_number(value):
    if not value.isdecimal() or len(value) != 10:
        raise ValidationError(
            _('Не верный номер паспорта. Укажите его в формате 9999999999')
        )
