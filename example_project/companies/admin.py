from companies.models import Company, Contact
from django.contrib import admin
from django.views.generic import DetailView

from djadmin_detail_view.mixins import AdminChangeListViewDetail, AdminDetailMixin
from djadmin_detail_view.template_helpers import col, detail, details_table_for, table_for


# Register your models here.
@admin.register(Company)
class CompanyAdmin(AdminChangeListViewDetail, admin.ModelAdmin):
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

        ctx["dropdown_menu"] = [
            {"label": "Visit Google", "url": "https://www.google.com", "target": "_blank", "confirm": "Go to Google?"},
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
                ],
            },
        ]

        return ctx


@admin.register(Contact)
class ContactAdmin(AdminChangeListViewDetail, admin.ModelAdmin):
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

        ctx["layout"] = [
            {
                "row": [
                    {"col": contact_details},
                    {"col": company_details},
                ],
            },
        ]

        return ctx
