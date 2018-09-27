from rest_framework.reverse import reverse
from rest_framework import status

from .mixins import CreditAPITestCaseWithUsers
from .utils import build_absolute_url


class CompanyViewTestCase(CreditAPITestCaseWithUsers):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.objects_list_url = reverse('api:company-list')
        cls.partner_company_url = reverse('api:company-detail',
                                          kwargs={'pk': cls.partner_company.id})
        cls.co_company_url = reverse('api:company-detail',
                                     kwargs={'pk': cls.co_company.id})

    def test_list(self):
        # Супеопользователи видят все компании
        response = self.client_superuser.get(self.objects_list_url)
        self.assertEqual(response.data['count'], 2)

        # Пользователи, не привязанные к компаниям, не видят ни одной компании
        response = self.client_anyuser.get(self.objects_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Партнеры видят только свои компании
        response = self.client_partner.get(self.objects_list_url)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.partner_company.id)

        # КО видят только свои компании
        response = self.client_co.get(self.objects_list_url)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.co_company.id)

    def test_list_fields(self):
        """Проверяем, что api возвращает все поля, необходимые для отображения списка"""

        response = self.client_partner.get(self.objects_list_url)
        object_as_dict = response.data['results'][0]

        valid_list_item_dict = {
            "id": self.partner_company.id,
            "url": build_absolute_url(
                reverse('api:company-detail', kwargs={'pk': self.partner_company.id})),
            "name": "Partner Company",
        }

        self.assertDictEqual(object_as_dict, valid_list_item_dict)

    def test_detail_permissions(self):
        """Проверка прав на просмотр детальной информации
        """

        company_urls = [self.partner_company_url, self.co_company_url]

        # Суперпользователь видит всех

        for company_url in company_urls:
            response = self.client_superuser.get(company_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Пользователи, не привязанные к компаниям, не видят ничего
        for company_url in company_urls:
            response = self.client_anyuser.get(company_url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Партнеры видят только свои компании
        response = self.client_partner.get(self.partner_company_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client_partner.get(self.co_company_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # КО видят только свои компании
        response = self.client_co.get(self.co_company_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client_co.get(self.partner_company_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        # Супеопользователи не могут создавать
        response = self.client_superuser.post(self.objects_list_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Пользователи, не привязанные к компаниям, не могут создавать
        response = self.client_anyuser.post(self.objects_list_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Партнеры не могут создавать
        response = self.client_partner.post(self.objects_list_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # КО не могут создавать
        response = self.client_co.post(self.objects_list_url, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        """Удаление
        """
        response = self.client_superuser.delete(self.partner_company_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put(self):
        """PUT
        """
        response = self.client_superuser.put(self.partner_company_url, data={})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch(self):
        """PATCH
        """
        response = self.client_superuser.patch(self.partner_company_url, data={})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
