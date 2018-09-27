from django.db import models
from django.utils import timezone


class OfferQuerySet(models.QuerySet):

    def active(self):
        # Предположил, что ротация - это промежуток времени, когда кредитное предложение актуально.
        # Соответственно фильтруем предложения по данным полям.
        now = timezone.now()
        return self.filter(rotation_start__lte=now, rotation_end__gte=now)

    def not_active(self):
        now = timezone.now()
        return self.exclude(rotation_start__lte=now, rotation_end__gte=now)


class OfferManager(models.Manager):

    def get_queryset(self):
        return OfferQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def not_active(self):
        return self.get_queryset().not_active()
