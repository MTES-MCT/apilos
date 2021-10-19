import os
import errno

from django.http.response import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.files.storage import default_storage

from core import settings
from .models import UploadedFile, UploadedFileSerializer


def _compute_dirpath(request):
    if "convention" in request.POST:
        uuid = request.POST["convention"]
        object_name = "conventions"
    elif "programme" in request.POST:
        uuid = request.POST["programme"]
        object_name = "programmes"
    else:
        raise Exception(
            "/upload path should be called with a programme of convention parameter"
        )
    return f"{object_name}/{uuid}/media/"


@require_GET
def display_file(request, convention_uuid, uploaded_file_uuid):
    uploaded_file = UploadedFile.objects.get(uuid=uploaded_file_uuid)

    if uploaded_file.dirpath:
        filepath = (
            f"{uploaded_file.dirpath}/{uploaded_file.uuid}_{uploaded_file.filename}"
        )
    else:
        filepath = (
            f"conventions/{convention_uuid}/media/"
            + f"{uploaded_file.uuid}_{uploaded_file.filename}"
        )

    print(filepath)
    file = default_storage.open(
        filepath,
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
    dirpath = _compute_dirpath(request)

    for file in files.values():
        # compute path
        uploaded_file = UploadedFile.objects.create(
            filename=file.name,
            size=file.size,
            dirpath=dirpath,
            content_type=file.content_type,
        )
        handle_uploaded_file(uploaded_file, file)
        uploaded_file.save()
        uploaded_files.append(UploadedFileSerializer(uploaded_file).data)
    return JsonResponse({"success": "true", "uploaded_file": uploaded_files})


def handle_uploaded_file(uploaded_file, file):
    # with default_storage.open(f'media/{uploaded_file.uuid}', 'w') as destination:

    if settings.DEFAULT_FILE_STORAGE == "django.core.files.storage.FileSystemStorage":
        if not os.path.exists(settings.MEDIA_URL + uploaded_file.dirpath):
            try:
                os.makedirs(settings.MEDIA_URL + uploaded_file.dirpath)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

    destination = default_storage.open(
        f"{uploaded_file.dirpath}/{uploaded_file.uuid}_{uploaded_file.filename}",
        "bw",
    )
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
