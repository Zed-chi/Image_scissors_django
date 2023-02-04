import os
import shutil
from datetime import datetime

from django.apps import AppConfig
from django.conf import settings
from django.core.signals import request_started


def my_callback(sender, **kwargs):
    now = datetime.now()
    up = [
        f"{settings.IMAGES_UPLOAD_DIR}/{i}"
        for i in os.listdir(settings.IMAGES_UPLOAD_DIR)
    ]
    res = [f"Result/{i}" for i in os.listdir("Result")]
    for file in up + res:
        created_at = datetime.fromtimestamp(os.stat(file).st_ctime)
        if (now - created_at).seconds > settings.IMG_LIFE_SEC:
            shutil.rmtree(file)
            # os.removedirs(file)


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"

    def ready(self):
        request_started.connect(my_callback)
