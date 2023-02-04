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
    dir = os.path.join(settings.MEDIA_ROOT, session_id)
    url = f"{settings.MEDIA_URL}{session_id}"
    image_files = os.listdir(dir)
    images_info = [{"name": i, "url": f"{url}/{i}"} for i in image_files]    
    context = {"images": images_info, "session": session_id}

    return render(request, "main/editor.html", context)


def process_images(request):
    """ renders Editor page for your images list """
    if not request.method == "POST":
        return redirect("main:index")
    if not request.POST.get("process"):
        return redirect("main:index")
    s_id = request.POST.get("session")
    print(request.POST["process"])
    dir = os.path.join(settings.MEDIA_ROOT, s_id)
    image_files = os.listdir(dir)
    values = json.loads(request.POST["process"])
    for file in image_files:
        attrs = values[file]
        filepath = os.path.join(dir, file)
        im = Image.open(filepath)
        width, height = im.size
        rows = int(attrs["row"])
        cols = int(attrs["col"])
        img_width = round((width / 100) * (int(attrs["width"]) / cols))
        img_height = round((height / 100) * (int(attrs["height"]) / rows))
        left_offset = round((width / 100) * (int(attrs["left"])))
        top_offset = round((height / 100) * (int(attrs["top"])))

        # Создание изображений
        result_dir = f"IMAGES_RESULT_DIR/{s_id}"
        os.makedirs(result_dir, exist_ok=True)
        for row in range(rows):
            for col in range(cols):
                region = im.crop(
                    [
                        left_offset,
                        top_offset,
                        left_offset + img_width,
                        top_offset + img_height,
                    ]
                )
                name, ext = file.split(".")
                tile_path = (
                    f"{result_dir}/{name}-{left_offset}-{top_offset}.{ext}"
                )
                region.save(tile_path)
                left_offset += img_width
            top_offset += img_height
    result_images = os.listdir(result_dir)
    with ZipFile(f"{settings.IMAGES_RESULT_DIR}{s_id}.zip", "w") as arc:
        for path in result_images:
            arc.write(f"{result_dir}/{path}")
    try:
        with open(f"{s_id}.zip", "rb") as arc:
            file_data = arc.read()
        response = HttpResponse(file_data, content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{s_id}.zip"'
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
    path = os.path.join(settings.MEDIA_ROOT, user_id, image.name)
    os.makedirs(
        os.path.join(settings.MEDIA_ROOT, user_id),
        exist_ok=True
    )
    with open(path, "wb") as file:
        file.write(image.read())