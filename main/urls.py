from django.urls import path

from . import views


app_name = "main"
urlpatterns = [
    path("submit_images", views.submit_images, name="submit_images"),
    path("editor/<str:session_id>", views.edit_images, name="edit_images"),
    path("process", views.process_images, name="process_images"),
    path("", views.index, name="index"),
]
