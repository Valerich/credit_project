import datetime

from django.contrib.auth import get_user_model

import factory
import factory.django
import factory.fuzzy

from credit_project.loans.models import Company, Borrower, Offer, CreditRequest
from .utils import get_tz_datetime

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.fuzzy.FuzzyText(length=12)
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')
    is_superuser = False

    class Meta:
        model = User


class CompanyFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=12)
    user = factory.SubFactory(UserFactory)
    kind = factory.fuzzy.FuzzyChoice(Company.KIND._db_values)

    class Meta:
        model = Company


class BorrowerFactory(factory.django.DjangoModelFactory):
    last_name = factory.fuzzy.FuzzyText(length=12)
    first_name = factory.fuzzy.FuzzyText(length=12)
    middle_name = factory.fuzzy.FuzzyText(length=12)
    birth_date = factory.fuzzy.FuzzyDate(start_date=datetime.date(2010, 1, 1))
    phone_number = '+79998887766'
    passport_number = '9999999999'
    score = factory.fuzzy.FuzzyInteger(0, 1000)
    company = factory.SubFactory(CompanyFactory)

    class Meta:
        model = Borrower


class OfferFactory(factory.django.DjangoModelFactory):
    name = factory.fuzzy.FuzzyText(length=12)
    company = factory.SubFactory(CompanyFactory)
    rotation_start = factory.fuzzy.FuzzyDateTime(start_dt=get_tz_datetime(2010, 1, 1))
    rotation_end = factory.fuzzy.FuzzyDateTime(start_dt=get_tz_datetime(2010, 1, 1))
    kind = factory.fuzzy.FuzzyChoice(Offer.KIND._db_values)
    min_score = factory.fuzzy.FuzzyInteger(0, 200)
    max_score = factory.fuzzy.FuzzyInteger(200, 1000)

    class Meta:
        model = Offer


class CreditRequestFactory(factory.django.DjangoModelFactory):
    status = factory.fuzzy.FuzzyChoice(CreditRequest.STATUSES._db_values)
    borrower = factory.SubFactory(BorrowerFactory)
    offer = factory.SubFactory(OfferFactory)

    class Meta:
        model = CreditRequest
