from example_project.tests.conftest_admin import AdminTestMixin
from example_project.tests.conftest_ssl_server import BrowserSslLiveServerTestCase
from example_project.tests.conftest_webpacked import UseRealWebpackmixin


class TestAdminDetailView(AdminTestMixin, UseRealWebpackmixin, BrowserSslLiveServerTestCase):
    def test_visit_company_detail(self):
        assert 1 == 1
