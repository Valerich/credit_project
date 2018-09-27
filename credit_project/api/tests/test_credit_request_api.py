from unittest import mock
import datetime

from django.forms.models import model_to_dict
from rest_framework.reverse import reverse
from rest_framework import status

from credit_project.api.tests.factories import CompanyFactory, BorrowerFactory, OfferFactory, \
    CreditRequestFactory
from credit_project.loans.models import Company, CreditRequest
from .mixins import CreditAPITestCaseWithUsers
from .utils import build_absolute_url, get_tz_datetime


class CreditRequestViewTestCase(CreditAPITestCaseWithUsers):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.objects_list_url = reverse('api:credit_request-list')

    def test_list(self):
        self.create_default_credit_requests()

        # Супеопользователи видят все
        response = self.client_superuser.get(self.objects_list_url)
        self.assertEqual(response.data['count'], 4)

        # Пользователи, не привязанные к компаниям, не видят ничего
        response = self.client_anyuser.get(self.objects_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Партнеры видят только свои
        response = self.client_partner.get(self.objects_list_url)
        self.assertEqual(response.data['count'], 2)
        ids = {item['id'] for item in response.data['results']}
        self.assertEqual(ids, {self.credit_request_1_1.id, self.credit_request_1_2.id})

        # КО видят только свои
        response = self.client_co.get(self.objects_list_url)
        self.assertEqual(response.data['count'], 2)
        ids = {item['id'] for item in response.data['results']}
        self.assertEqual(ids, {self.credit_request_1_1.id, self.credit_request_2_1.id})

    @mock.patch('django.utils.timezone.now')
    def test_list_fields(self, now_mock):
        """Проверяем, что api возвращает все поля, необходимые для отображения списка"""

        now_mock.return_value = get_tz_datetime(2010, 6, 1)

        credit_company = CompanyFactory(
            user=self.anyuser,
            kind=Company.KIND.credit_organization
        )
        partner_company = CompanyFactory(
            kind=Company.KIND.partner
        )
        borrower = BorrowerFactory(
            last_name='Last Name',
            first_name='First Name',
            middle_name='Middle Name',
            birth_date=datetime.date(2010, 1, 1),
            phone_number='+79991112233',
            passport_number='9999999999',
            score=100,
            company=partner_company,
        )
        offer = OfferFactory(company=credit_company)

        credit_request = CreditRequestFactory(
            status=CreditRequest.STATUSES.new,
            borrower=borrower,
            offer=offer
        )

        response = self.client_anyuser.get(self.objects_list_url)

        object_as_dict = response.data['results'][0]

        valid_list_item_dict = {
            "id": credit_request.id,
            "created": "2010-06-01T04:00:00+04:00",
            "status": "new",
            "sent_date": None,
            "url": build_absolute_url(
                reverse('api:credit_request-detail', kwargs={'pk': credit_request.id})),
            "offer": offer.id,
            "offer_url": build_absolute_url(
                reverse('api:offer-detail', kwargs={'pk': offer.id})),
            "borrower": borrower.id,
            "borrower_detail": {
                "id": borrower.id,
                "url": build_absolute_url(
                    reverse('api:borrower-detail', kwargs={'pk': borrower.id})),
                "last_name": "Last Name",
                "first_name": "First Name",
                "middle_name": "Middle Name",
                "birth_date": "2010-01-01",
                "phone_number": "+79991112233",
                "passport_number": "9999999999",
                "score": 100,
                "company": partner_company.id,
                "company_url": build_absolute_url(
                    reverse('api:company-detail', kwargs={'pk': partner_company.id})),
            }
        }

        self.assertDictEqual(object_as_dict, valid_list_item_dict)

    def test_detail_permissions(self):
        """Проверка прав на просмотр детальной информации
        """
        self.create_default_credit_requests()

        all_urls = {
            self.credit_request_1_1_url,
            self.credit_request_1_2_url,
            self.credit_request_2_1_url,
            self.credit_request_2_2_url,
        }

        partner_urls = {
            self.credit_request_1_1_url,
            self.credit_request_1_2_url,
        }
        credit_organization_urls = {
            self.credit_request_1_1_url,
            self.credit_request_2_1_url,
        }

        # Суперпользователи видят всех
        for url in all_urls:
            response = self.client_superuser.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Пользователи, не привязанные к компаниям, не видят ничего
        for url in all_urls:
            response = self.client_anyuser.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Партнеры видят только свои компании
        for url in partner_urls:
            response = self.client_partner.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        for url in all_urls - partner_urls:
            response = self.client_partner.get(url)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # КО видят только свои компании
        for url in credit_organization_urls:
            response = self.client_co.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        for url in all_urls - credit_organization_urls:
            response = self.client_co.get(url)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete(self):
        """Удаление
        """

        self.create_default_credit_requests()

        # Партнеры удалять не могут
        response = self.client_partner.delete(self.credit_request_1_1_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CreditRequest.objects.filter(id=self.credit_request_1_1.id).exists())

        # КО удалять не могут
        response = self.client_co.delete(self.credit_request_1_1_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CreditRequest.objects.filter(id=self.credit_request_1_1.id).exists())

        # Пользователи, не привязанные к компаниям, удалять не могут
        response = self.client_anyuser.delete(self.credit_request_1_1_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CreditRequest.objects.filter(id=self.credit_request_1_1.id).exists())

        # Суперпользователь может удалять
        response = self.client_superuser.delete(self.credit_request_1_1_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CreditRequest.objects.filter(id=self.credit_request_1_1.id).exists())

    def test_put(self):
        """PUT
        """

        self.create_default_credit_requests()

        credit_request_as_dict = model_to_dict(self.credit_request_1_1)
        credit_request_as_dict['status'] = CreditRequest.STATUSES.issued

        # Партнерам запрещено
        response = self.client_partner.put(self.credit_request_1_1_url, credit_request_as_dict)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # КО разрешено
        response = self.client_co.put(self.credit_request_1_1_url, credit_request_as_dict)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Пользователям, не привязанным к компаниям, запрещено
        response = self.client_anyuser.put(self.credit_request_1_1_url, credit_request_as_dict)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Суперпользователям разрешено
        response = self.client_superuser.put(self.credit_request_1_1_url, credit_request_as_dict)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch(self):
        """PATCH
        """

        self.create_default_credit_requests()

        credit_request_as_dict = model_to_dict(self.credit_request_1_1)
        credit_request_as_dict['status'] = CreditRequest.STATUSES.issued

        # Партнерам запрещено
        response = self.client_partner.patch(self.credit_request_1_1_url, credit_request_as_dict)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # КО разрешено обновлять своих
        response = self.client_co.patch(self.credit_request_1_1_url, credit_request_as_dict)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client_co.patch(self.credit_request_1_2_url, credit_request_as_dict)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Пользователям, не привязанным к компаниям, запрещено
        response = self.client_anyuser.patch(self.credit_request_1_1_url, credit_request_as_dict)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Суперпользователям разрешено
        response = self.client_superuser.patch(self.credit_request_1_1_url, credit_request_as_dict)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_co_can_update_only_status(self):
        """Проверяем, что кредитные организации могут обновлять только статус"""

        self.create_default_credit_requests()

        # Сначала тестируем patch
        credit_request_as_dict = model_to_dict(self.credit_request_1_1)
        credit_request_as_dict['offer'] = self.offer2.id
        credit_request_as_dict['borrower'] = self.borrower2.id
        credit_request_as_dict['sent_date'] = '2018-01-01'
        credit_request_as_dict['status'] = CreditRequest.STATUSES.issued

        response = self.client_co.patch(self.credit_request_1_1_url, credit_request_as_dict)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.credit_request_1_1.refresh_from_db()
        self.assertEqual(self.credit_request_1_1.status, CreditRequest.STATUSES.issued)
        self.assertEqual(self.credit_request_1_1.offer_id, self.offer.id)
        self.assertEqual(self.credit_request_1_1.borrower_id, self.borrower.id)
        self.assertEqual(self.credit_request_1_1.sent_date, None)

        # а потом put
        credit_request_as_dict['status'] = CreditRequest.STATUSES.approved

        response = self.client_co.put(self.credit_request_1_1_url, credit_request_as_dict)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.credit_request_1_1.refresh_from_db()
        self.assertEqual(self.credit_request_1_1.status, CreditRequest.STATUSES.approved)
        self.assertEqual(self.credit_request_1_1.offer_id, self.offer.id)
        self.assertEqual(self.credit_request_1_1.borrower_id, self.borrower.id)
        self.assertEqual(self.credit_request_1_1.sent_date, None)

    def create_default_credit_requests(self):
        self.partner2_company = CompanyFactory(
            name='Partner 2 Company',
            kind=Company.KIND.partner,
        )
        self.co2_company = CompanyFactory(
            name='Credit Organization 2 Company',
            kind=Company.KIND.credit_organization,
        )

        self.borrower = BorrowerFactory(company=self.partner_company)
        self.borrower2 = BorrowerFactory(company=self.partner2_company)

        self.offer = OfferFactory(company=self.co_company,
                                  rotation_start=get_tz_datetime(1990, 1, 1),
                                  rotation_end=get_tz_datetime(2100, 1, 1))
        self.offer2 = OfferFactory(company=self.co2_company)

        self.credit_request_1_1 = CreditRequestFactory(
            borrower=self.borrower,
            offer=self.offer,
        )
        self.credit_request_1_2 = CreditRequestFactory(
            borrower=self.borrower,
            offer=self.offer2,
        )
        self.credit_request_2_1 = CreditRequestFactory(
            borrower=self.borrower2,
            offer=self.offer,
        )
        self.credit_request_2_2 = CreditRequestFactory(
            borrower=self.borrower2,
            offer=self.offer2,
        )

        self.credit_request_1_1_url = reverse('api:credit_request-detail',
                                              kwargs={'pk': self.credit_request_1_1.id})
        self.credit_request_1_2_url = reverse('api:credit_request-detail',
                                              kwargs={'pk': self.credit_request_1_2.id})
        self.credit_request_2_1_url = reverse('api:credit_request-detail',
                                              kwargs={'pk': self.credit_request_2_1.id})
        self.credit_request_2_2_url = reverse('api:credit_request-detail',
                                              kwargs={'pk': self.credit_request_2_2.id})
