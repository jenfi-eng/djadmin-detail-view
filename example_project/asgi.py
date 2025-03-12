"""
ASGI config for Jenfi Partners project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/asgi/

"""

import logging
import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application

logger = logging.getLogger(__name__)

# This allows easy placement of apps within the interior
# partners_app directory.
ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(ROOT_DIR / "apps"))

# If DJANGO_SETTINGS_MODULE is unset, default to the local settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example_project.settings")

# This application object is used by any ASGI server configured to use this file.
application = get_asgi_application()
