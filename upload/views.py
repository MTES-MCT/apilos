import base64
import re

from io import BytesIO
from PIL import Image

from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.files.storage import default_storage

from core import settings
from .models import UploadedFile, UploadedFileSerializer


@require_GET
def display_file(request, convention_uuid, uploaded_file_uuid):
    uploaded_file = UploadedFile.objects.get(uuid=uploaded_file_uuid)

    file = default_storage.open(
        f"conventions/{convention_uuid}/media/{uploaded_file.uuid}_{uploaded_file.filename}",
        "rb",
    )

    data = file.read()
    file.close()

    response = HttpResponse(
        data,
        content_type=uploaded_file.content_type,
    )
    response["Content-Disposition"] = f"attachment; filename={uploaded_file.filename}"
    return response


@require_POST
def upload_file(request):
    files = request.FILES
    uploaded_files = []
    convention_uuid = request.POST["convention"]

    for file in files.values():
        uploaded_file = UploadedFile.objects.create(
            filename=file.name,
            size=file.size,
            thumbnail=thumbnail(file),
            content_type=file.content_type,
        )
        handle_uploaded_file(uploaded_file, file, convention_uuid)
        uploaded_file.save()
        uploaded_files.append(UploadedFileSerializer(uploaded_file).data)
    return JsonResponse({"success": "true", "uploaded_file": uploaded_files})


def handle_uploaded_file(uploaded_file, file, convention_uuid):
    # with default_storage.open(f'media/{uploaded_file.uuid}', 'w') as destination:
    destination = default_storage.open(
        f"conventions/{convention_uuid}/media/{uploaded_file.uuid}_{uploaded_file.filename}",
        "w",
    )
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()


def thumbnail(file):
    content_type = file.content_type
    match_types = re.findall(r"image/([A-Za-z]+)", content_type)
    thumbnail_format = "PNG"
    if len(match_types):
        thumbnail_format = match_types[0].upper()
        img_file = file.file
    elif content_type == "application/pdf":
        img_file = settings.BASE_DIR / "static/img/pdf.png"
        content_type = "image/png"
    else:
        img_file = settings.BASE_DIR / "static/img/img.png"
        content_type = "image/png"

    thumbnail_size = 120, 120
    data_img = BytesIO()
    img = Image.open(img_file)
    img.thumbnail(thumbnail_size)

    img.save(data_img, format=thumbnail_format)

    return "data:{};base64,{}".format(
        content_type, base64.b64encode(data_img.getvalue()).decode("utf-8")
    )
