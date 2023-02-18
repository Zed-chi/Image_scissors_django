import os
import shutil
from datetime import datetime
from os.path import isdir, isfile

from django.apps import AppConfig
from django.conf import settings
from django.core.signals import request_started


def my_callback(sender, **kwargs):
    now = datetime.now()
    up = [
        f"{settings.BASE_DIR}/{settings.IMAGES_UPLOAD_DIR}/{i}"
        for i in os.listdir(
            os.path.join(settings.BASE_DIR, settings.IMAGES_UPLOAD_DIR)
        )
    ]
    res = [
        f"{settings.BASE_DIR}/{settings.IMAGES_RESULT_DIR}/{i}"
        for i in os.listdir(
            os.path.join(settings.BASE_DIR, settings.IMAGES_RESULT_DIR)
        )
    ]
    for elem in up + res:
        created_at = datetime.fromtimestamp(os.stat(elem).st_ctime)
        if (now - created_at).seconds > settings.IMG_LIFE_SEC:
            if isdir(elem):
                shutil.rmtree(elem)
            if isfile(elem):
                os.remove(elem)


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"

    def ready(self):
        request_started.connect(my_callback)
