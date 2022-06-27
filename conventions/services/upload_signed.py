import os
import errno

from django.views.decorators.http import require_POST
from django.core.files.storage import default_storage

from django.conf import settings
from conventions.forms import ConventionSignedFileForm


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


def handle_uploaded_file(f):
    destination = default_storage.open(
        "convention/xxx_signed",
        "bw",
    )
    for chunk in f.chunks():
        destination.write(chunk)


@require_POST
def upload_file(request):
    files = request.FILES
    dirpath = _compute_dirpath(request)
    for file in files.values():

        # compute path
        uploaded_file = ConventionSignedFileForm.objects.create(
            dirpath=dirpath,
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
            f"{uploaded_file.dirpath}/{uploaded_file.uuid}_signed",
            "bw",
        )
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()

        uploaded_file.save()
