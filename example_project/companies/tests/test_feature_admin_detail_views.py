from django.urls import reverse
from faker import Faker

from example_project.companies.tests.factories import CompanyFactory, ContactFactory, UserFactory
from example_project.tests.conftest_ssl_server import BrowserSslLiveServerTestCase
from example_project.tests.conftest_webpacked import UseRealWebpackmixin


class TestAdminDetailView(UseRealWebpackmixin, BrowserSslLiveServerTestCase):
    def setUp(self):
        super().setUp()

        admin_pw = Faker().password()
        admin_user = UserFactory(is_staff=True, is_superuser=True, password=admin_pw)

        self.goto(reverse("admin:login"))

        self.page.fill("#id_username", admin_user.username)
        self.page.fill("#id_password", admin_pw)
        self.page.wait_for_selector("input[type=submit]").click()

        self.company = CompanyFactory()

        for _ in range(5):
            ContactFactory(company=self.company)

    def test_visit_company_detail(self):
        page = self.page

        page.wait_for_selector("text=Companys").click()

        view_link_selector = 'text="View"'
        page.wait_for_selector(view_link_selector)
        page.click(view_link_selector)

        page.wait_for_selector("h1").assert_text(self.company.name)
