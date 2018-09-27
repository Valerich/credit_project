import datetime
from unittest import mock

from django.forms.models import model_to_dict

from rest_framework.reverse import reverse
from rest_framework import status

from credit_project.loans.models import Company, Borrower, Offer
from .factories import BorrowerFactory, CompanyFactory, OfferFactory
from .mixins import CreditAPITestCaseWithUsers
from .utils import build_absolute_url, get_tz_datetime


class OfferViewTestCase(CreditAPITestCaseWithUsers):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.objects_list_url = reverse('api:offer-list')

    @mock.patch('django.utils.timezone.now')
    def test_list_permissions(self, now_mock):
        now_mock.return_value = get_tz_datetime(2010, 6, 1)

        self.create_offers()

        # Супеопользователи видят всеx
        response = self.client_superuser.get(self.objects_list_url)
        self.assertEqual(response.data['count'], 2)

        # Пользователи, не привязанные к компаниям, не видят никого
        response = self.client_anyuser.get(self.objects_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Партнеры видят всех
        response = self.client_partner.get(self.objects_list_url)
        self.assertEqual(response.data['count'], 2)

        # КО не видят никого
        response = self.client_co.get(self.objects_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('django.utils.timezone.now')
    def test_list_fields(self, now_mock):
        """Проверяем, что api возвращает все поля, необходимые для отображения списка"""

        now_mock.return_value = get_tz_datetime(2010, 6, 1)

        self.create_co_offer()

        response = self.client_partner.get(self.objects_list_url)
        object_as_dict = response.data['results'][0]

        self.assertDictEqual(object_as_dict, self.co_offer_as_dict)

    def test_detail_permissions(self):
        """Проверка прав на просмотр детальной информации
        """

        self.create_offers()

        urls = [self.co_offer_url, self.co2_offer_url]

        # Суперпользователь видит всех
        for url in urls:
            response = self.client_superuser.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Пользователи, не привязанные к компаниям, не видят ничего
        for url in urls:
            response = self.client_anyuser.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Партнеры не видят ничего
        for url in urls:
            response = self.client_anyuser.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # КО не видят ничего
        for url in urls:
            response = self.client_anyuser.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create(self):
        """Создание
        """

        new_offer_data = {
            "name": "Новое предложение",
            "company": self.co_company.id,
            "rotation_start": "2010-01-01",
            "rotation_end": "2011-01-01",
            "kind": "consumer_credit",
            "min_score": 100,
            "max_score": 1000,
        }

        # Партнеры не могут создавать
        response = self.client_partner.post(self.objects_list_url, new_offer_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertFalse(Offer.objects.all().exists())

        # КО не могут создавать
        response = self.client_co.post(self.objects_list_url, new_offer_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Offer.objects.all().exists())

        # Пользователи, не привязанные к компаниям, не могут создавать
        response = self.client_anyuser.post(self.objects_list_url, new_offer_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Offer.objects.all().exists())

        # Суперпользователь не может создавать
        response = self.client_superuser.post(self.objects_list_url, new_offer_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertFalse(Offer.objects.all().exists())

    def test_delete(self):
        """Удаление
        """

        offer = OfferFactory()
        offer_url = reverse('api:borrower-detail', kwargs={'pk': offer.id})

        # Партнеры удалять не могут
        response = self.client_partner.delete(offer_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Offer.objects.filter(id=offer.id).exists())

        # КО удалять не могут
        response = self.client_co.delete(offer_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Offer.objects.filter(id=offer.id).exists())

        # Пользователи, не привязанные к компаниям, удалять не могут
        response = self.client_anyuser.delete(offer_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Offer.objects.filter(id=offer.id).exists())

        # Суперпользователь не может удалять
        response = self.client_superuser.delete(offer_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Offer.objects.filter(id=offer.id).exists())

    def test_put(self):
        """PUT
        """

        new_name = 'New name'

        offer = OfferFactory()
        offer_url = reverse('api:borrower-detail', kwargs={'pk': offer.id})
        offer_as_dict = model_to_dict(offer)
        offer_as_dict['name'] = new_name

        # Партнерам запрещено
        response = self.client_partner.put(offer_url, offer_as_dict)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # КО запрещено
        response = self.client_co.put(offer_url, offer_as_dict)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Пользователям, не привязанным к компаниям, запрещено
        response = self.client_anyuser.put(offer_url, offer_as_dict)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Суперпользователям запрещено
        response = self.client_superuser.put(offer_url, offer_as_dict)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch(self):
        """PATCH
        """

        new_name = 'New name'

        offer = OfferFactory()
        offer_url = reverse('api:borrower-detail', kwargs={'pk': offer.id})
        offer_as_dict = model_to_dict(offer)
        offer_as_dict['name'] = new_name

        # Партнерам запрещено
        response = self.client_partner.patch(offer_url, offer_as_dict)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # КО запрещено
        response = self.client_co.patch(offer_url, offer_as_dict)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Пользователям, не привязанным к компаниям, запрещено
        response = self.client_anyuser.patch(offer_url, offer_as_dict)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Суперпользователям запрещено
        response = self.client_superuser.patch(offer_url, offer_as_dict)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def get_list_active(self):
        """Отдаем только те предложения, которые активны на текущую дату"""

        with mock.patch('django.utils.timezone.now', get_tz_datetime(2010, 6, 1)) as i:
            # На 2010-06-01 активно 2 предложения
            response = self.client_superuser.get(self.objects_list_url)
            self.assertEqual(response.data['count'], 2)

        with mock.patch('django.utils.timezone.now', get_tz_datetime(2018, 6, 1)) as i:
            # На 2018-06-01 все предложения просрочены
            response = self.client_superuser.get(self.objects_list_url)
            self.assertEqual(response.data['count'], 0)


    def create_offers(self):
        self.create_co_offer()
        self.create_co2_offer()

    def create_co_offer(self):
        self.co_offer = OfferFactory(
            name='Супер предложение',
            company=self.co_company,
            rotation_start=get_tz_datetime(2010, 1, 1),
            rotation_end=get_tz_datetime(2011, 1, 1),
            kind=Offer.KIND.consumer_credit,
            min_score=100,
            max_score=1000,
        )

        self.co_offer_url = reverse('api:offer-detail',
                                    kwargs={'pk': self.co_offer.id})

        self.co_offer_as_dict = {
            "id": self.co_offer.id,
            "url": build_absolute_url(self.co_offer_url),
            "name": "Супер предложение",
            "company": self.co_company.id,
            "company_url": build_absolute_url(
                reverse('api:company-detail', kwargs={'pk': self.co_company.id})),
            "rotation_start": "2010-01-01T03:00:00+03:00",
            "rotation_end": "2011-01-01T03:00:00+03:00",
            "kind": "consumer_credit",
            "min_score": 100,
            "max_score": 1000,
        }

    def create_co2_offer(self):
        self.co2_company = CompanyFactory(kind=Company.KIND.credit_organization)

        self.co2_offer = OfferFactory(
            name='Супер предложение2',
            company=self.co2_company,
            rotation_start=get_tz_datetime(2010, 1, 1),
            rotation_end=get_tz_datetime(2011, 1, 1),
            kind=Offer.KIND.consumer_credit,
            min_score=100,
            max_score=1000,
        )

        self.co2_offer_url = reverse('api:offer-detail',
                                    kwargs={'pk': self.co2_offer.id})
