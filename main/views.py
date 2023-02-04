import json
import os
import os.path
from datetime import datetime
from zipfile import ZipFile

from django.conf import settings
from django.http import (HttpResponse, HttpResponseNotFound)
from django.shortcuts import redirect, render, reverse
from PIL import Image


def index(request):
    """ renders Index Page """
    return render(request, "main/loadpage.html")


def edit_images(request, session_id):
    """ renders Editor page for your images list """
    upl_dir = os.path.join(settings.IMAGES_UPLOAD_DIR, session_id)
    url = f"{settings.MEDIA_URL}{session_id}"
    image_files = os.listdir(upl_dir)
    images_info = [
        {"name": image, "url": f"{url}/{image}"}
        for image in image_files
    ]
    context = {"images": images_info, "session": session_id}
    return render(request, "main/editor.html", context)


def process_images(request):
    """ renders Editor page for your images list """
    if not request.method == "POST":
        return redirect("main:index")
    if "process" not in request.POST:
        return redirect("main:index")

    session_id = request.POST.get("session")
    upl_dir = os.path.join(settings.IMAGES_UPLOAD_DIR, session_id)
    image_filenames = os.listdir(upl_dir)
    values = json.loads(request.POST["process"])

    for filename in image_filenames:
        attrs = values[filename]
        filepath = os.path.join(upl_dir, filename)
        image = Image.open(filepath)
        width, height = image.size
        rows = int(attrs["row"])
        cols = int(attrs["col"])
        img_width = round((width / 100) * (int(attrs["width"]) / cols))
        img_height = round((height / 100) * (int(attrs["height"]) / rows))
        left_offset = round((width / 100) * (int(attrs["left"])))
        top_offset = round((height / 100) * (int(attrs["top"])))

        # Создание изображений
        result_dir = f"{settings.IMAGES_RESULT_DIR}/{session_id}"
        os.makedirs(result_dir, exist_ok=True)
        for row in range(rows):
            for col in range(cols):
                region = image.crop(
                    [
                        left_offset,
                        top_offset,
                        left_offset + img_width,
                        top_offset + img_height,
                    ]
                )
                name, ext = filename.split(".")
                tile_path = (
                    f"{result_dir}/{name}-{left_offset}-{top_offset}.{ext}"
                )
                region.save(tile_path)
                left_offset += img_width
            top_offset += img_height
    result_images = os.listdir(result_dir)
    with ZipFile(f"{settings.IMAGES_RESULT_DIR}{session_id}.zip", "w") as arc:
        for path in result_images:
            arc.write(f"{result_dir}/{path}")
    try:
        with open(f"{session_id}.zip", "rb") as arc:
            file_data = arc.read()
        response = HttpResponse(file_data, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{session_id}.zip"'
    except IOError:
        response = HttpResponseNotFound("<h1>File not exist</h1>")
    return response


def submit_images(request):
    """ renders """
    if "images" not in request.FILES:
        return redirect(reverse("main:index"))

    session_id = str(datetime.now().timestamp())
    images = request.FILES.getlist("images")

    try:
        for image in images:
            save_image(image, session_id)
    except IOError as e:
        return HttpResponse(e)
    finally:
        return redirect("main:edit_images", session_id=session_id)


def save_image(image, user_id):
    """ saving image file """
    path = os.path.join(settings.IMAGES_UPLOAD_DIR, user_id, image.name)
    os.makedirs(
        os.path.join(settings.IMAGES_UPLOAD_DIR, user_id),
        exist_ok=True
    )
    with open(path, "wb") as file:
        file.write(image.read())
