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
    elif "lot" in request.POST:
        uuid = request.POST["lot"]
        object_name = "lots"
    else:
        raise Exception(
            "/upload path should be called with a programme, lot or convention parameter"
        )
    return f"{object_name}/{uuid}/media/"


@require_GET
def display_file(request, convention_uuid, uploaded_file_uuid):
    uploaded_file = UploadedFile.objects.get(uuid=uploaded_file_uuid)

    file = default_storage.open(
        uploaded_file.filepath(convention_uuid),
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

        if (
            settings.DEFAULT_FILE_STORAGE
            == "django.core.files.storage.FileSystemStorage"
        ):
            if not os.path.exists(settings.MEDIA_URL + dirpath):
                try:
                    os.makedirs(settings.MEDIA_URL + dirpath)
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

        uploaded_file.save()
        uploaded_files.append(UploadedFileSerializer(uploaded_file).data)
    return JsonResponse({"success": "true", "uploaded_file": uploaded_files})
