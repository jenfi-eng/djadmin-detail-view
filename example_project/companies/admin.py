from django.contrib import admin
from django.views.generic import DetailView
from moneyed import Money
from simple_history.admin import SimpleHistoryAdmin

from djadmin_detail_view.mixins import AdminChangeListViewDetail, AdminDetailMixin
from djadmin_detail_view.template_helpers import (
    col,
    detail,
    details_table_for,
    dropdown_item,
    table_for,
    top_menu_btn,
)
from example_project.companies.models import Company, Contact


# Register your models here.
@admin.register(Company)
class CompanyAdmin(AdminChangeListViewDetail, SimpleHistoryAdmin):
    list_display = ("id", "name", "address")

    def get_default_detail_view(self):
        return CompanyDetailView


class CompanyDetailView(AdminDetailMixin, DetailView):
    model = Company

    def get_context_data(self, request, *args, **kwargs):
        ctx = super().get_context_data(request, *args, **kwargs)

        company_details = details_table_for(
            panel_name="Company Details",
            obj=self.object,
            details=[
                detail("id"),
                detail("name"),
                detail("address"),
                detail("total_completed_order_amount", value=lambda x: x.total_order_value()),
                detail("Test Money", value=Money(0, "USD")),
            ],
        )

        contact_list = table_for(
            panel_name="Contact List",
            obj_set=self.object.contact_set.all(),
            cols=[
                col("id"),
                col("name"),
                col("phone"),
                col("email"),
                col("created_at"),
                col("updated_at"),
                col("is_active"),
                col("none", value=lambda x: None),
            ],
        )

        contact_list_empty = table_for(
            panel_name="Empty LIst",
            obj_set=self.object.contact_set.none(),
            cols=[
                col("id"),
                col("name"),
                col("phone"),
                col("email"),
                col("created_at"),
                col("updated_at"),
                col("is_active"),
                col("none", value=lambda x: None),
            ],
        )

        # Lazy-loaded contact list for testing lazy loading functionality
        contact_list_lazy = table_for(
            panel_name="Lazy Loaded Contacts",
            obj_set=self.object.contact_set.all(),
            cols=[col("id"), col("name"), col("email")],
            lazy_load=True,
            lazy_key="contacts_lazy",
        )

        ctx["top_menu_buttons"] = [
            top_menu_btn(
                "Download PDF",
                url=f"https://www.google.com/search?q={self.object.name}",
                btn_class="btn-primary",
                target="_blank",
            ),
            top_menu_btn(
                "Archive",
                url=f"/admin/companies/company/{self.object.id}/delete/",
                confirm="Are you sure you want to archive this company?",
            ),
        ]

        ctx["dropdown_menu"] = [
            dropdown_item(
                "Visit Google",
                url="https://www.google.com",
                target="_blank",
                confirm="Go to Google?",
            ),
            dropdown_item(
                "Export Data",
                url=f"/admin/companies/company/{self.object.id}/change/",
            ),
        ]

        ctx["layout"] = [
            {
                "row": [
                    {"col": company_details},
                    {"col": None},
                ],
            },
            {"header": "Contacts"},
            {
                "row": [
                    {"col": contact_list},
                    {"col": contact_list_empty},
                ],
            },
            {"header": "Lazy Loaded Section"},
            {
                "row": [
                    {"col": contact_list_lazy},
                ],
            },
        ]

        return ctx

    def lazy_contacts_lazy(self):
        """Method called by LazyFragmentView to render the lazy-loaded contacts."""
        return table_for(
            panel_name="Lazy Loaded Contacts",
            obj_set=self.object.contact_set.all(),
            cols=[col("id"), col("name"), col("email")],
        )


@admin.register(Contact)
class ContactAdmin(AdminChangeListViewDetail, SimpleHistoryAdmin):
    def get_default_detail_view(self):
        return ContactDetailView


class ContactDetailView(AdminDetailMixin, DetailView):
    model = Contact

    def get_context_data(self, request, *args, **kwargs):
        ctx = super().get_context_data(request, *args, **kwargs)

        contact_details = details_table_for(
            panel_name="Contact Details",
            obj=self.object,
            details=[
                detail("id"),
                detail("name"),
                detail("phone"),
                detail("email"),
                detail("created_at"),
                detail("updated_at"),
                detail("is_active"),
            ],
        )

        company_details = details_table_for(
            panel_name="Company Details",
            obj=self.object.company,
            details=[
                detail("id"),
                detail("name"),
                detail("address"),
                detail("total_completed_order_amount", value=lambda x: x.total_order_value()),
            ],
        )

        ctx["top_menu_buttons"] = [
            top_menu_btn(
                "Edit Contact",
                url=f"/admin/companies/contact/{self.object.id}/change/",
                btn_class="btn-primary",
            ),
            top_menu_btn(
                "Delete",
                url=f"/admin/companies/contact/{self.object.id}/delete/",
                btn_class="btn-danger",
                confirm="Are you sure you want to delete this contact?",
            ),
        ]

        ctx["dropdown_menu"] = [
            dropdown_item(
                "View Company",
                url=f"/admin/companies/company/{self.object.company.id}/",
            ),
            dropdown_item(
                "Send Email",
                url=f"mailto:{self.object.email}",
                target="_blank",
            ),
            dropdown_item(
                "Call Phone",
                url=f"tel:{self.object.phone}",
            ),
        ]

        ctx["layout"] = [
            {
                "row": [
                    {"col": contact_details},
                    {"col": company_details},
                ],
            },
        ]

        return ctx
