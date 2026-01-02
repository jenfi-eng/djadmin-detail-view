from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpResponse
from django.template.loader import render_to_string
from django.urls import path
from django.utils.html import format_html
from django.views import View

from .url_helpers import admin_lazy_path_for, admin_path_for, admin_path_name


class AdminChangeListViewDetail:
    default_detail_view = None

    def get_default_detail_view(self):
        if self.default_detail_view:
            return self.default_detail_view

        raise ValueError("Please define default_detail_view. Recommended: override `get_default_detail_view` method.")

    def get_urls(self):
        default_urls = super().get_urls()

        urls = self._remove_default_detail_redirect(default_urls)
        urls = self._add_default_detail(urls)
        urls = self._add_lazy_fragment_url(urls)

        return urls

    def _remove_default_detail_redirect(self, urls):
        cleaned_urls = [
            url
            for url in urls
            if not (url.name is None and url.lookup_str == "django.views.generic.base.RedirectView")
        ]
        return cleaned_urls

    def _add_default_detail(self, urls):
        detail_view = self.get_default_detail_view()

        detail_path = path(
            f"<{detail_view.pk_url_kwarg}>/",
            self.admin_site.admin_view(detail_view.as_view(admin_obj=self)),
            name=admin_path_name(detail_view.model, "detail"),
        )

        return urls + [detail_path]

    def _add_lazy_fragment_url(self, urls):
        detail_view = self.get_default_detail_view()

        lazy_path = path(
            f"<{detail_view.pk_url_kwarg}>/lazy/<str:fragment_key>/",
            self.admin_site.admin_view(
                LazyFragmentView.as_view(
                    admin_obj=self,
                    detail_view_class=detail_view,
                )
            ),
            name=admin_path_name(detail_view.model, "lazy_fragment"),
        )

        return urls + [lazy_path]

    def get_list_display(self, request):
        list_display = super().get_list_display(request)

        list_display_list = list(list_display)

        if "view_details" in list_display_list:
            list_display_list.remove("view_details")

        list_display_list.insert(1, "view_details")

        return tuple(list_display_list)

    @admin.display(description="View Details")
    def view_details(self, obj):
        url = admin_path_for(obj, action="detail")
        return format_html('<a href="{}">View</a>', url)


class AdminDetailMixin:
    template_name = "admin/djadmin_components/auto_layout_detail.html"
    admin_obj = None

    def get(self, request, *args, **kwargs):
        self._validate_admin_obj()
        self.object = self.get_object()
        context = self.get_context_data(request, *args, object=self.object, **kwargs)
        return self.render_to_response(context)

    def _validate_admin_obj(self):
        if self.admin_obj is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} requires 'admin_obj' to be set. "
                "Use AdminChangeListViewDetail on your ModelAdmin and call "
                "DetailView.as_view(admin_obj=self) when registering the URL."
            )
        if not isinstance(self.admin_obj, AdminChangeListViewDetail):
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} requires the ModelAdmin to use "
                f"AdminChangeListViewDetail mixin. Got {self.admin_obj.__class__.__name__} instead."
            )

    def get_context_data(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        admin_base_context = dict(
            # This will make the left side bar navigation appear with all controls.
            self.admin_obj.admin_site.each_context(request),
            opts=self.model._meta,
            app_label=self.model._meta.app_label,
            title=self.object,
            original=self.object,
            has_view_permission=self.admin_obj.has_view_permission(request, self.object),
            # Inject lazy URL helper for templates
            admin_lazy_path_for=admin_lazy_path_for,
        )
        return context | admin_base_context


class LazyFragmentView(View):
    """
    View that renders lazy-loaded fragments for admin detail pages.

    This view is automatically registered by AdminChangeListViewDetail
    and handles AJAX requests to load table_for/details_table_for content.

    The fragment_key corresponds to a method on the DetailView named
    lazy_{fragment_key}() that returns the actual table/details data.
    """

    admin_obj = None
    detail_view_class = None

    def get(self, request, pk, fragment_key):
        # Reconstruct the detail view to access lazy methods
        detail_view = self.detail_view_class()
        detail_view.admin_obj = self.admin_obj
        detail_view.request = request
        detail_view.kwargs = {"pk": pk}

        # Get the object
        try:
            detail_view.object = detail_view.get_object()
        except Exception:
            raise Http404(f"Object with pk={pk} not found")

        # Call the lazy_{fragment_key} method
        method_name = f"lazy_{fragment_key}"
        if not hasattr(detail_view, method_name):
            raise Http404(f"Lazy fragment method '{method_name}' not found on {detail_view.__class__.__name__}")

        fragment_data = getattr(detail_view, method_name)()

        # Determine which template to use based on fragment structure
        if isinstance(fragment_data, dict) and "rows" in fragment_data:
            template = "admin/djadmin_components/object_list.html"
            context = {"object_list": fragment_data}
        else:
            template = "admin/djadmin_components/object_details.html"
            context = {"object_details": fragment_data}

        html = render_to_string(template, context, request=request)
        return HttpResponse(html)
