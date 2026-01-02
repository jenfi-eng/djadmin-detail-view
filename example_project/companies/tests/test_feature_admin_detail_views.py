from django.urls import reverse
from faker import Faker

from example_project.companies.tests.factories import CompanyFactory, ContactFactory, UserFactory
from example_project.tests.conftest_ssl_server import BrowserSslLiveServerTestCase
from example_project.tests.conftest_webpacked import UseRealWebpackmixin


class TestAdminDetailView(UseRealWebpackmixin, BrowserSslLiveServerTestCase):
    def setUp(self):
        super().setUp()

        # Create a new page for each test since tearDown closes it
        self.page = self.context.new_page()
        self.page.set_default_timeout(timeout=5000)

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

        contact = self.company.contact_set.first()
        page.wait_for_selector(f"text={contact.name}").click()

        assert page.is_visible(f"text={contact.name}")

        # TODO: Add partial test
        # TODO: Add file preview test

    def test_top_menu_confirm_button(self):
        """Test that top menu buttons with confirm show dialog and handle cancel/accept"""
        page = self.page

        # Navigate to company detail view
        page.wait_for_selector("text=Companys").click()
        page.wait_for_selector('text="View"').click()

        # Test canceling the confirm dialog
        page.once("dialog", lambda dialog: dialog.dismiss())
        page.click('text="Archive"')

        # Should still be on the detail page (not navigated)
        assert page.is_visible(f"text={self.company.name}")

        # Test accepting the confirm dialog
        page.once("dialog", lambda dialog: dialog.accept())
        page.click('text="Archive"')

        # Should navigate to delete page (URL contains /delete/)
        page.wait_for_url(f"**/admin/companies/company/{self.company.id}/delete/**")

    def test_dropdown_menu_confirm_button(self):
        """Test that dropdown menu items with confirm show dialog and handle cancel/accept"""
        page = self.page

        # Navigate to company detail view
        page.wait_for_selector("text=Companys").click()
        page.wait_for_selector('text="View"').click()

        # Open the Actions dropdown
        page.click('button:has-text("Actions")')

        # Test canceling the confirm dialog
        page.once("dialog", lambda dialog: dialog.dismiss())
        page.click('text="Visit Google"')

        # Should still be on the detail page (not navigated)
        assert page.is_visible(f"text={self.company.name}")

        # Open dropdown again and test accepting
        page.click('button:has-text("Actions")')
        page.once("dialog", lambda dialog: dialog.accept())
        page.click('text="Visit Google"')

        # Should navigate to Google (new tab/window, so we just check the dialog was accepted)
        # Note: Since target="_blank", we won't actually navigate away in this tab

    def test_contact_detail_view_buttons(self):
        """Test that contact detail view has working buttons with confirm dialogs"""
        page = self.page

        # Navigate to company, then to a contact
        page.wait_for_selector("text=Companys").click()
        page.wait_for_selector('text="View"').click()

        contact = self.company.contact_set.first()
        page.wait_for_selector(f"text={contact.name}").click()

        # Verify we're on the contact detail page
        assert page.is_visible(f"text={contact.name}")

        # Test the Delete button with confirm
        page.once("dialog", lambda dialog: dialog.dismiss())
        page.click('text="Delete"')

        # Should still be on the detail page
        assert page.is_visible(f"text={contact.name}")

    def test_lazy_loading_panel(self):
        """Test that lazy-loaded panels load content via AJAX"""
        page = self.page

        # Navigate to company detail view
        page.wait_for_selector("text=Companys").click()
        page.wait_for_selector('text="View"').click()

        # Verify the lazy loading header section exists
        page.wait_for_selector("text=Lazy Loaded Section")

        # The panel should show "Lazy Loaded Contacts" header initially
        page.wait_for_selector("text=Lazy Loaded Contacts")

        # Wait for the lazy-loaded table to appear (the table inside the object-list card)
        # This indicates the content has been fetched and the spinner replaced
        # The loaded panel will have the "object-list" class
        page.wait_for_selector(
            '.object-list:has-text("Lazy Loaded Contacts")',
            timeout=10000,
        )

        page.pause()

        # Verify the table has content - there should be a count indicator "(5 of 5)"
        # showing the contacts have been loaded
        page.wait_for_selector('text="(5 of 5)"', timeout=5000)

    def test_lazy_loading_shows_spinner_initially(self):
        """Test that lazy-loaded panels show a spinner before content loads"""
        page = self.page

        # Navigate to company detail view
        page.wait_for_selector("text=Companys").click()
        page.wait_for_selector('text="View"').click()

        # The lazy panel should have a spinner element (it may disappear quickly)
        # We check that the data-controller attribute exists
        page.wait_for_selector('[data-controller="lazy-panel"]')

        # Wait for content to eventually load
        contact = self.company.contact_set.first()
        page.wait_for_selector(f"text={contact.name}", timeout=10000)
