from django.test import override_settings
from django.urls import reverse
from faker import Faker
from playwright.sync_api import Page

from djadmin_detail_view.url_helpers import admin_path_for

from ..companies.tests.factories import UserFactory


class AdminTestMixin:
    def _admin_login_page(self) -> Page:
        admin_pw = Faker().password()
        admin_user = UserFactory(is_staff=True, is_superuser=True, password=admin_pw)

        # log admin to backend
        admin_context = self.browser.new_context(ignore_https_errors=True)
        admin_page = admin_context.new_page()
        admin_page.set_default_timeout(timeout=5000)
        self._admin_goto(admin_page, "admin:login")

        admin_page.fill("#id_username", admin_user.email)
        admin_page.fill("#id_password", admin_pw)

        admin_page.wait_for_selector("input[type=submit]").click()

        return admin_page

    def _admin_goto(self, admin_page, obj_or_route, action=None):
        route = self._produce_route(obj_or_route, action=action)

        admin_page.goto(self.live_server_url.replace("app", "internal") + route)

    @override_settings(DEFAULT_HOST="internal", ROOT_URLCONF="config.urls.internal")
    def _produce_route(self, obj, action):
        if isinstance(obj, str):
            return reverse(obj)
        else:
            return admin_path_for(obj, action=action)
