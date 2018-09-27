from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.choices import Choices
from phonenumber_field.modelfields import PhoneNumberField

from .managers import OfferManager
from .validators import validate_passport_number

User = get_user_model()


class Company(models.Model):
    KIND = Choices(
        ('credit_organization', _('Кредитная организация')),
        ('partner', _('Партнер')),
    )
    name = models.CharField(_('Название'), max_length=255)
    user = models.OneToOneField(User, verbose_name=_('Пользователь'))
    kind = models.CharField(_('Тип организации'), choices=KIND, max_length=20)

    class Meta:
        verbose_name = _('Компания')
        verbose_name_plural = _('Компании')
        ordering = ('name', )

    def __str__(self):
        return self.name

    @property
    def is_partner(self):
        return self.kind == self.KIND.partner

    @property
    def is_credit_organization(self):
        return self.kind == self.KIND.credit_organization


class Offer(models.Model):
    KIND = Choices(
        ('consumer_credit', _('Потребительский кредит')),
        ('mortgage', _('Ипотека')),
        ('car_loan', _('Автокредит')),
    )
    created = models.DateTimeField(_('Создано'), auto_now_add=True)
    modified = models.DateTimeField(_('Изменено'), auto_now=True)
    name = models.CharField(_('Название'), max_length=255)
    company = models.ForeignKey(Company,
                                verbose_name=_('Кредитная организация'),
                                on_delete=models.PROTECT)
    rotation_start = models.DateTimeField(_('Начало ротации'))
    rotation_end = models.DateTimeField(_('Окончание ротации'))
    kind = models.CharField(_('Тип предложения'), choices=KIND, max_length=20)
    min_score = models.PositiveSmallIntegerField(_('Минимальный скоринговый балл'))
    max_score = models.PositiveSmallIntegerField(_('Максимальный скоринговый балл'))

    objects = OfferManager()

    class Meta:
        verbose_name = _('Предложение')
        verbose_name_plural = _('Предложения')
        ordering = ('-created', )

    def __str__(self):
        return '{} ({})'.format(self.name, self.company.name)


class Borrower(models.Model):
    created = models.DateTimeField(_('Создана'), auto_now_add=True)
    modified = models.DateTimeField(_('Изменена'), auto_now=True)

    last_name = models.CharField(_('Фамилия'), max_length=255)
    first_name = models.CharField(_('Имя'), max_length=255)
    middle_name = models.CharField(_('Отчество'), max_length=255)
    birth_date = models.DateField(_('Дата рождения'))
    phone_number = PhoneNumberField(_('Номер телефона'))
    passport_number = models.CharField(_('Номер паспорта'), max_length=10,
                                       validators=[validate_passport_number, ])

    score = models.PositiveSmallIntegerField(_('Скоринговый балл'))
    company = models.ForeignKey(Company, verbose_name=_('Партнер'), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Анкета клиента')
        verbose_name_plural = _('Анкеты клиентов')
        ordering = ('-created', )

    def __str__(self):
        return '{} {} {}'.format(self.last_name, self.first_name, self.middle_name)


class CreditRequest(models.Model):
    STATUSES = Choices(
        ('new', _('Новая')),
        ('sent', _('Отправлена')),
        ('received', _('Получена')),
        ('approved', _('Одобрено')),
        ('denied', _('Отказано')),
        ('issued', _('Выдано'))
    )
    status = models.CharField(_('Статус'), choices=STATUSES, default=STATUSES.new, max_length=20)
    created = models.DateTimeField(_('Создана'), auto_now_add=True)
    sent_date = models.DateTimeField(_('Отправлена'), blank=True, null=True)
    borrower = models.ForeignKey(Borrower, verbose_name=_('Анкета клиента'),
                                 on_delete=models.PROTECT)
    offer = models.ForeignKey(Offer, verbose_name=_('Предложение'),
                              on_delete=models.PROTECT)

    class Meta:
        verbose_name = _('Заявка в КО')
        verbose_name_plural = _('Заявки в КО')
        ordering = ('-created', )

    def __str__(self):
        return 'CreditRequest: {} / {}'.format(self.id, self.status)
