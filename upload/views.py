import base64

from io import BytesIO
from PIL import Image

from django.http.response import JsonResponse
from django.views.decorators.http import require_POST

from .models import UploadedFile, UploadedFileSerializer


@require_POST
def upload_file(request):
    files = request.FILES
    uploaded_files = []
    for file in files.values():
        uploaded_file = UploadedFile.objects.create(
            filename=file.name,
            size=file.size,
            thumbnail=thumbnail(file),
            content_type=file.content_type,
        )
        print(uploaded_file.thumbnail)
        handle_uploaded_file(uploaded_file, file)
        uploaded_file.save()
        uploaded_files.append(UploadedFileSerializer(uploaded_file).data)
    return JsonResponse({"success": "true", "uploaded_file": uploaded_files})


def handle_uploaded_file(uploaded_file, file):
    with open(f"media/{uploaded_file.uuid}", "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def thumbnail(file):

    print(file.content_type)

    thumbnail_size = 120, 120
    data_img = BytesIO()
    img = Image.open(file.file)
    img.thumbnail(thumbnail_size)

    img.save(data_img, format="BMP")

    return "data:image/jpg;base64,{}".format(
        base64.b64encode(data_img.getvalue()).decode("utf-8")
    )
