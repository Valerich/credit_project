from rest_framework.test import APITestCase, APIClient

from credit_project.loans.models import Company
from .factories import UserFactory, CompanyFactory


class CreditAPITestCaseWithUsers(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.superuser = UserFactory(username='admin', is_superuser=True)
        cls.partner_user = UserFactory(username='partner_user')
        cls.co_user = UserFactory(username='credit_organization_user')
        cls.anyuser = UserFactory(username='any_user')

        cls.partner_company = CompanyFactory(name='Partner Company',
                                             kind=Company.KIND.partner,
                                             user=cls.partner_user)
        cls.co_company = CompanyFactory(name='Credit Organization Company',
                                        kind=Company.KIND.credit_organization,
                                        user=cls.co_user)

    def setUp(self):
        self.client_partner = APIClient()
        self.client_partner.login(username=self.partner_user.username, password='defaultpassword')
        self.client_co = APIClient()
        self.client_co.login(username=self.co_user.username, password='defaultpassword')
        self.client_superuser = APIClient()
        self.client_superuser.login(username=self.superuser.username, password='defaultpassword')
        self.client_anyuser = APIClient()
        self.client_anyuser.login(username=self.anyuser.username, password='defaultpassword')

    def tearDown(self):
        self.client_partner.session.clear()
        self.client_co.session.clear()
        self.client_superuser.session.clear()
        self.client_anyuser.session.clear()
