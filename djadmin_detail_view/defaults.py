from django.conf import settings

TEMPLATE_TIME_FORMAT = getattr(settings, "TEMPLATE_TIME_FORMAT", "d M Y, P O")
