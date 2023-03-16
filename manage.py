#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from django.conf import settings


def make_dirs():
    upl_path = os.path.join(os.getcwd(), settings.IMAGES_UPLOAD_DIR)
    res_path = os.path.join(os.getcwd(), settings.IMAGES_RESULT_DIR)
    os.makedirs(upl_path, exist_ok=True)
    os.makedirs(res_path, exist_ok=True)


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "image_scissors.settings")
    make_dirs()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

