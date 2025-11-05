# Django Admin Detail View

Django Admin's missing `DetailView`.

Allows easy creation of a `DetailView` via DSL for an object in Django Admin.

![Companies' changelist added View](images/changelist.png)

![Company's DetailView](images/detail_view_company.png)

![Contact's DetailView](images/detail_view_contact.png)

## Why this exists

Django Admin's is missing detail views (by design). It's strengths lie in administering specific objects via form modification.

But, a common need is to allow internal staff/admins to view specific objects and and their related objects. Historically the recommendation was to build a separate website/frontend for this.

## Theory

With models `Company`, `ContactInfo`, `SalesLeads`, `Orders`, Internal staff want to quickly understand the status of a particular `Company` so a simple View displaying these 4 objects is very beneficial.

Then I can drill down into a `Order` and see all related `Product`s, `OrderStatusUpdate`s, `SalesComments`.

Via DSL, it is fast to stand up `DetailView`s for many objects.

## Beliefs

Information dense, grid layout. Function over form.

## Features

- Add View button to `changelist` for Object.
- `detail_table_for()` builds object's details table.
- `table_for()` builds a list of
- `ctx["layout"]` holds the grid structure.

## Pre-reqs

- Bootstrap as Webpack
- webpack_loader

## Install

1. Direct add github to `pyproject.toml`, `git@github.com:jenfi-eng/djadmin-detail-view.git`.
1. Add to `INSTALLED_APPS`
1. Create a `DetailView` and add mixin `AdminDetailMixin`
1. To the object's admin add `AdminChangeListViewDetail` and function `get_default_detail_view`
1. Return the newly created DetailView in `get_default_detail_view`.

See `example_project/companies/admin.py` for reference.

## Code Example

```python
from django.contrib import admin
from djadmin_detail_view.views import AdminChangeListViewDetail, AdminDetailMixin

from my_app.companies.models import Company

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
                detail("legal_name"),
                detail("tax_id"),
                detail("total_completed_order_amount", value=lambda x: x.total_order_value()),
            ]
        )

        orders_list = table_for(
            panel_name="Orders",
            obj_set=self.object.order_set.all(),
            cols=[
                col("id"),
                col("legal_name"),
                col("total_value"),
                col("created"),
            ]
        )

        ctx["layout"] = [
            {
                "row": [
                    {"col": company_details},
                    {"col": None},
                ],
            },
        ]
```

## Template Helper API Reference

### Layout Helpers

#### `details_table_for(*, obj, details, panel_name=None)`

Creates a detail table for displaying attributes of a single object.

**Parameters:**
- `obj`: The object to display details for
- `details`: List of detail/col definitions
- `panel_name`: Optional panel title

**Example:**
```python
company_details = details_table_for(
    panel_name="Company Details",
    obj=self.object,
    details=[
        detail("id"),
        detail("legal_name"),
        detail("created"),
    ]
)
```

#### `detail(col_name, display_name=None, value=None, help_text=None)`

Defines a single detail/column in a details table.

**Parameters:**
- `col_name`: Field name or attribute path (e.g., "name" or "user.email")
- `display_name`: Optional display label (auto-generated from col_name if not provided)
- `value`: Optional callable or static value to override field value
- `help_text`: Optional help text to display

**Example:**
```python
detail("id")
detail("legal_name", display_name="Company Name")
detail("total_revenue", value=lambda obj: obj.calculate_total_revenue())
detail("status", help_text="Current company status")
```

**Alias:** `col()` is an alias for `detail()`

#### `table_for(*, panel_name=None, obj_set, obj_set_limit=10, cols, actions=None, readonly=None, view_all_url=None, view_all_footer_url=None, allow_edit=False, add_url=None, add_label=None, count=None)`

Creates a list table for displaying multiple related objects.

**Parameters:**
- `obj_set`: QuerySet or list of objects to display
- `cols`: List of col/detail definitions for columns
- `panel_name`: Optional panel title
- `obj_set_limit`: Maximum number of rows to display (default: 10)
- `actions`: Optional list of action functions that take an object and return a menu item
- `view_all_url`: Optional URL to view all items
- `view_all_footer_url`: Optional URL shown in footer
- `allow_edit`: Boolean to show edit controls
- `add_url`: Optional URL to add new items
- `add_label`: Optional label for add button
- `count`: Optional count override

**Example:**
```python
orders_list = table_for(
    panel_name="Orders",
    obj_set=self.object.order_set.all(),
    obj_set_limit=20,
    cols=[
        col("id"),
        col("total_value"),
        col("created"),
    ],
    actions=[
        lambda obj: dropdown_item("View", url=admin_url_for(obj, "detail")),
    ],
    add_url=reverse("admin:orders_order_add"),
)
```

### Menu Helpers

#### `top_menu_btn(label, url, *, btn_class="btn-secondary", html_attrs=None, target=None, confirm=None, css_class=None)`

Creates a button for the top menu bar.

**Parameters:**
- `label`: Button text
- `url`: Button URL
- `btn_class`: Bootstrap button class (default: "btn-secondary")
- `html_attrs`: Dict of HTML attributes
- `target`: Link target attribute (e.g., "_blank")
- `confirm`: Confirmation message to show before navigation
- `css_class`: Additional CSS classes

**Example:**
```python
context["top_menu_buttons"] = [
    top_menu_btn("Export PDF", url="/export/pdf/", btn_class="btn-primary"),
    top_menu_btn("Delete", url="/delete/", btn_class="btn-danger", confirm="Are you sure?"),
]
```

#### `dropdown_item(label, url, *, html_attrs=None, target=None, confirm=None, css_class=None)`

Creates an item for the Actions dropdown menu. Alias for `menu_item()`.

**Parameters:**
- `label`: Item text
- `url`: Item URL
- `html_attrs`: Dict of HTML attributes
- `target`: Link target attribute
- `confirm`: Confirmation message to show before navigation
- `css_class`: Additional CSS classes

**Example:**
```python
context["dropdown_menu"] = [
    dropdown_item("Edit", url="/edit/"),
    dropdown_item("Delete", url="/delete/", confirm="Are you sure?"),
    dropdown_item("View on Site", url="/public/", target="_blank"),
]
```

#### `dropdown_divider()`

Creates a horizontal divider line in the dropdown menu.

**Example:**
```python
context["dropdown_menu"] = [
    dropdown_item("Edit", url="/edit/"),
    dropdown_divider(),
    dropdown_item("Delete", url="/delete/"),
]
```

#### `dropdown_header(label)`

Creates a non-interactive header/label in the dropdown menu.

**Parameters:**
- `label`: Header text to display

**Example:**
```python
context["dropdown_menu"] = [
    dropdown_header("Admin Actions"),
    dropdown_item("Edit", url="/edit/"),
    dropdown_item("Delete", url="/delete/"),
    dropdown_divider(),
    dropdown_header("External Links"),
    dropdown_item("View on Website", url="/site/"),
]
```

### Auto-formatting

The `detail()` and `col()` helpers automatically format common data types:

- **DateTime**: Formatted using `TEMPLATE_TIME_FORMAT` setting
- **Date**: Formatted using Django's `SHORT_DATE_FORMAT`
- **Money** (moneyed library): Formatted with currency symbol if available
- **ImageFieldFile**: Rendered as `<img>` tag with max dimensions 100x100px
- **None**: Displayed as "-"
- **Model instances**: Auto-linked to admin detail view if col_name is in `AUTOLINK_COL_NAMES` (default: `["id", "legal_name"]`)

## Current Open Source Status

This project is not ready for wider consumption. It is currently built for Jenfi and its internal needs. Thus, it has specific requirements such as `django-hosts` that may need to be abstracted away.

PRs are welcome to make it more generally accessible.

## VSCode

### Testing

Add config to allow specs to be run inside VSCode.

```javascript
// .vscode/settings.json
{
  "python.testing.pytestArgs": [
    ""
  ],
  "python.testing.unittestEnabled": false,
  "python.testing.pytestEnabled": true,
}

```

### Web Launch Config

```javascript
{
    "name": "Django Web",
    "type": "python",
    "request": "launch",
    "program": "${workspaceFolder}/server.py",
    "args": [],
    "django": true,
    "justMyCode": false
},
```

## TODO

1. Add specs.
1. Versioning and release on pypi.
1. Allow non-webpack based installs.

## Credit

This project takes a lot of inspiration from Rail's [ActiveAdmin](https://github.com/activeadmin/activeadmin) and its DSL.
