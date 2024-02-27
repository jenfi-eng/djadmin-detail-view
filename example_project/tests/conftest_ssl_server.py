import logging
import os
from pathlib import Path
from urllib.parse import urlparse

import environ
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from django.test.testcases import LiveServerTestCase, LiveServerThread, QuietWSGIRequestHandler
from django.utils.functional import classproperty
from playwright.sync_api import sync_playwright
from sslserver.management.commands.runsslserver import SecureHTTPServer, WSGIRequestHandler

from example_project.companies.tests.factories import UserFactory

logger = logging.getLogger(__name__)


class SecureQuietWSGIRequestHandler(WSGIRequestHandler, QuietWSGIRequestHandler):
    pass


class SecureLiveServerThread(LiveServerThread):
    def _create_server(self, connections_override=None):
        certs_path = Path(settings.ROOT_DIR, "tests", "test_certs")
        cert_file = certs_path / "lvh-cert.pem"
        key_file = certs_path / "lvh-key.pem"

        return SecureHTTPServer(
            (self.host, self.port),
            SecureQuietWSGIRequestHandler,
            cert_file,
            key_file,
        )


class SecureLiveServerTestCase(LiveServerTestCase):
    server_thread_class = SecureLiveServerThread


class BrowserSslLiveServerTestCase(StaticLiveServerTestCase):
    server_thread_class = SecureLiveServerThread
    host = "app.lvh.me"

    @classproperty
    def live_server_url(cls):
        url = super().live_server_url

        cls.parsed_url = urlparse(url)
        cls.server_port = cls.parsed_url.port

        return url.replace("http:", "https:")

    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()

        # Check if there is a get_host method, if there is, run it.
        if callable(getattr(cls, "get_host", None)):
            cls.host = cls.get_host()

        cls.playwright = sync_playwright().start()

        headless = environ.Env().bool("TEST_HEADLESS_BROWSER", default=True)
        cls.browser = cls.playwright.chromium.launch(headless=headless)
        cls.context = cls.browser.new_context(ignore_https_errors=True)

        cls.page = cls.context.new_page()
        cls.page.set_default_timeout(timeout=5000)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.close()
        cls.playwright.stop()

    def tearDown(self):
        if self.page:
            self.page.close()

    def goto(self, path, page=None):
        if page is None:
            page = self.page

        page.goto(f"{self.live_server_url}{path}")


class BrowserLogInSslTestCase(BrowserSslLiveServerTestCase):
    # Creates a User and logs them in
    # Makes page available to the spec
    def user_logged_in_page(self):
        self.user = UserFactory()
        self.company = self.user.company

        self._login_user_setup(self.user)

    def _login_user_setup(self, user):
        self.client = Client()
        self.client.force_login(user)

        cookies = self.client.cookies

        for cookie_name in cookies:
            self.context.add_cookies(
                [
                    {
                        "name": cookie_name,
                        "value": cookies[cookie_name].value,
                        "domain": self.host,
                        "path": "/",
                    }
                ]
            )
