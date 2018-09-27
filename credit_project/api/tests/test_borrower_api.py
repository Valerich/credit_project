import datetime

from rest_framework.reverse import reverse
from rest_framework import status

from credit_project.loans.models import Company, Borrower
from .factories import BorrowerFactory, CompanyFactory
from .mixins import CreditAPITestCaseWithUsers
from .utils import build_absolute_url


class BorrowerViewTestCase(CreditAPITestCaseWithUsers):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.objects_list_url = reverse('api:borrower-list')

        cls.partner2_company = CompanyFactory(kind=Company.KIND.partner)

        cls.partner_borrower = BorrowerFactory(
            last_name='Last Name',
            first_name='First Name',
            middle_name='Middle Name',
            birth_date=datetime.date(2010, 1, 1),
            phone_number='+79991112233',
            passport_number='9999999999',
            score=100,
            company=cls.partner_company,
        )
        cls.partner2_borrower = BorrowerFactory(
            last_name='Last Name 2',
            first_name='First Name 2',
            middle_name='Middle Name 2',
            birth_date=datetime.date(2010, 1, 1),
            phone_number='+79999999999',
            passport_number='8888888888',
            score=200,
            company=cls.partner2_company,
        )
        cls.partner_borrower_url = reverse('api:borrower-detail',
                                           kwargs={'pk': cls.partner_borrower.id})
        cls.partner2_borrower_url = reverse('api:borrower-detail',
                                            kwargs={'pk': cls.partner2_borrower.id})
        cls.partner_borrower_as_dict = {
            "id": cls.partner_borrower.id,
            "url": build_absolute_url(cls.partner_borrower_url),
            "last_name": "Last Name",
            "first_name": "First Name",
            "middle_name": "Middle Name",
            "birth_date": "2010-01-01",
            "phone_number": "+79991112233",
            "passport_number": "9999999999",
            "score": 100,
            "company": cls.partner_company.id,
            "company_url": build_absolute_url(
                reverse('api:company-detail', kwargs={'pk': cls.partner_company.id})),
        }

    def test_list(self):
        # Супеопользователи видят всеx
        response = self.client_superuser.get(self.objects_list_url)
        self.assertEqual(response.data['count'], 2)

        # Пользователи, не привязанные к компаниям, не видят никого
        response = self.client_anyuser.get(self.objects_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Партнеры видят только своиx
        response = self.client_partner.get(self.objects_list_url)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['company'], self.partner_company.id)

        # КО не видят никого
        response = self.client_co.get(self.objects_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_fields(self):
        """Проверяем, что api возвращает все поля, необходимые для отображения списка"""

        response = self.client_partner.get(self.objects_list_url)
        object_as_dict = response.data['results'][0]

        self.assertDictEqual(object_as_dict, self.partner_borrower_as_dict)
    #
    def test_detail_permissions(self):
        """Проверка прав на просмотр детальной информации
        """

        urls = [self.partner_borrower_url, self.partner2_borrower_url]

        # Суперпользователь видит всех
        for url in urls:
            response = self.client_superuser.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Пользователи, не привязанные к компаниям, не видят ничего
        for url in urls:
            response = self.client_anyuser.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Партнеры видят только свои компании
        response = self.client_partner.get(self.partner_borrower_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client_partner.get(self.partner2_borrower_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # КО не видят ничего
        for url in urls:
            response = self.client_anyuser.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create(self):
        data = {
            "last_name": "Last Name",
            "first_name": "First Name",
            "middle_name": "Middle Name",
            "birth_date": "2010-01-01",
            "phone_number": "+79991112233",
            "passport_number": "9999999999",
            "score": 100,
            "company": self.partner_company.id,
        }
        # Супеопользователи могут создавать
        response = self.client_superuser.post(self.objects_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Пользователи, не привязанные к компаниям, не могут создавать
        response = self.client_anyuser.post(self.objects_list_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Партнеры не могут создавать
        response = self.client_partner.post(self.objects_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # КО не могут создавать
        response = self.client_co.post(self.objects_list_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete(self):
        """Удаление
        """

        borrower = BorrowerFactory()
        borrower_url = reverse('api:borrower-detail', kwargs={'pk': borrower.id})

        # Партнеры удалять не могут
        response = self.client_partner.delete(borrower_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Borrower.objects.filter(id=borrower.id).exists())

        # КО удалять не могут
        response = self.client_co.delete(borrower_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Borrower.objects.filter(id=borrower.id).exists())

        # Пользователи, не привязанные к компаниям, удалять не могут
        response = self.client_anyuser.delete(borrower_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Borrower.objects.filter(id=borrower.id).exists())

        # Суперпользователь может удалять
        response = self.client_superuser.delete(borrower_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Borrower.objects.filter(id=borrower.id).exists())

    def test_put(self):
        """PUT
        """

        borrower = BorrowerFactory()
        borrower_url = reverse('api:borrower-detail', kwargs={'pk': borrower.id})

        # Партнерам запрещено
        response = self.client_partner.put(borrower_url, self.partner_borrower_as_dict)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # КО запрещено
        response = self.client_co.put(borrower_url, self.partner_borrower_as_dict)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Пользователям, не привязанным к компаниям, запрещено
        response = self.client_anyuser.put(borrower_url, self.partner_borrower_as_dict)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Суперпользователям разрешено
        response = self.client_superuser.put(borrower_url, self.partner_borrower_as_dict)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch(self):
        """PATCH
        """

        borrower = BorrowerFactory()
        borrower_url = reverse('api:borrower-detail', kwargs={'pk': borrower.id})

        # Партнерам запрещено
        response = self.client_partner.patch(borrower_url, self.partner_borrower_as_dict)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # КО запрещено
        response = self.client_co.patch(borrower_url, self.partner_borrower_as_dict)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Пользователям, не привязанным к компаниям, запрещено
        response = self.client_anyuser.patch(borrower_url, self.partner_borrower_as_dict)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Суперпользователям разрешено
        response = self.client_superuser.patch(borrower_url, self.partner_borrower_as_dict)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
