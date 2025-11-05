import copy
from datetime import date, datetime
from operator import attrgetter

from django.db.models.fields.files import ImageFieldFile
from django.utils import formats, timezone
from django.utils.html import format_html

from djadmin_detail_view.defaults import TEMPLATE_TIME_FORMAT

try:
    from moneyed import Money
except ImportError:
    Money = None

########################################################
# Jenfi Specific Helpers
########################################################
try:
    from apps.utils.money_format import humanize_money_with_currency
except ImportError:
    humanize_money_with_currency = None

from .url_helpers import auto_link
########################################################
# /Jenfi Specific Helpers
########################################################


def details_table_for(*, obj, details, panel_name=None):
    if obj:
        fill_missing_values(obj, details)

    return {
        "panel_name": panel_name,
        "obj": obj,
        "obj_details": details,
    }


def detail(col_name, display_name=None, value: any = None, help_text: str = None):
    if display_name is None:
        display_name = col_name.replace("_", " ").title()

    return {
        "col_name": col_name,
        "display_name": display_name,
        "value": value,
        "help_text": help_text,
    }


def table_for(
    *,
    panel_name=None,
    obj_set,
    obj_set_limit=10,
    cols,
    actions=None,
    readonly=None,
    view_all_url=None,
    view_all_footer_url=None,
    allow_edit=False,
    add_url=None,
    add_label=None,
    count=None,
):
    rows = []
    objs = obj_set

    if obj_set_limit:
        objs = objs[:obj_set_limit]

    # It's just like creating an attributes table
    for obj in objs:
        row = details_table_for(obj=obj, details=cols.copy())

        if actions:
            for action in actions:
                row.setdefault("actions", []).append(action(obj))

        rows.append(copy.deepcopy(row))

    if rows:
        count = len(obj_set) if isinstance(obj_set, list) else obj_set.count or "Many"
    else:
        count = 0

    0 if rows else (obj_set.count or len(obj_set) or "Many")

    return {
        "panel_name": panel_name,
        "cols": cols,
        "rows": rows,
        "view_all_url": view_all_url,
        "view_all_footer_url": view_all_footer_url,
        "obj_set_limit": obj_set_limit,
        "obj_set": obj_set,
        "allow_edit": allow_edit,
        "add_url": add_url,
        "add_label": add_label,
        "count": count,
    }


col = detail


def fill_missing_values(obj, rows):
    for row in rows:
        if _is_present(row["value"]):
            if callable(row["value"]):
                ret = row["value"](obj)
            else:
                ret = row["value"]
        else:
            ret = attrgetter(row["col_name"])(obj)

            ret = _attempt_to_turn_into_link(row, obj, ret)

        if isinstance(ret, datetime):
            ret = timezone.localtime(ret)
            ret = formats.date_format(ret, TEMPLATE_TIME_FORMAT)
        elif isinstance(ret, date):
            ret = formats.date_format(ret, format="SHORT_DATE_FORMAT")
        elif _is_money(ret) and humanize_money_with_currency is not None:
            ret = humanize_money_with_currency(ret)
        elif isinstance(ret, ImageFieldFile) and ret.name and ret.url:
            ret = format_html('<img src="{}" style="max-width: 100px; max-height: 100px;">', ret.url)
        elif ret is None:
            ret = "-"

        row["value_out"] = ret


# If the col name is "id/legal_name" or the result is an object with an admin path
# turn it into a link
AUTOLINK_COL_NAMES = ["id", "legal_name"]


def _attempt_to_turn_into_link(row, orig_obj, orig_ret):
    # Try to see if it's an object that has an admin path
    # If so, turn it into a link
    if row["col_name"] in AUTOLINK_COL_NAMES:
        curr_obj = orig_obj
    else:
        # ELSE try to see if it's an object that has an admin path
        curr_obj = orig_ret

    try:
        return auto_link(curr_obj, "detail")
    except Exception:
        pass

    return orig_ret


def _is_present(value):
    if value is None:
        return False
    if callable(value):
        return True
    if _is_money(value):
        return True
    if hasattr(value, "__len__"):  # strings, lists, dicts, etc.
        return bool(len(value))
    return bool(value)  # for other types


def _is_money(value):
    return Money is not None and isinstance(value, Money)


def menu_item(
    label,
    url,
    *,
    html_attrs=None,
    target=None,
    confirm=None,
    css_class=None,
):
    """
    Base helper to create a menu item (used by dropdown_item and top_menu_btn).

    Args:
        label: Item text
        url: Item URL
        html_attrs: Dict of HTML attributes to add to the element
        target: Link target attribute
        confirm: Confirmation message to show before navigation
        css_class: Additional CSS classes to add

    Returns:
        Dict with menu item configuration
    """
    return {
        "label": label,
        "url": url,
        "html_attrs": html_attrs,
        "target": target,
        "confirm": confirm,
        "class": css_class,
    }


dropdown_item = menu_item


def dropdown_divider():
    """
    Helper to create a dropdown divider (horizontal line separator).

    Returns:
        Dict with divider configuration
    """
    return {
        "type": "divider",
    }


def dropdown_header(label):
    """
    Helper to create a dropdown header (non-interactive label).

    Args:
        label: Header text to display

    Returns:
        Dict with header configuration
    """
    return {
        "type": "header",
        "label": label,
    }


def top_menu_btn(
    label,
    url,
    *,
    btn_class="btn-secondary",
    html_attrs=None,
    target=None,
    confirm=None,
    css_class=None,
):
    """
    Helper to create a top menu button.

    Args:
        label: Button text
        url: Button URL
        btn_class: Bootstrap button class (default: 'btn-secondary')
        html_attrs: Dict of HTML attributes to add to the element
        target: Link target attribute
        confirm: Confirmation message to show before navigation
        css_class: Additional CSS classes to add

    Returns:
        Dict with button configuration
    """
    item = menu_item(
        label=label,
        url=url,
        html_attrs=html_attrs,
        target=target,
        confirm=confirm,
        css_class=css_class,
    )
    item["btn_class"] = btn_class
    return item
