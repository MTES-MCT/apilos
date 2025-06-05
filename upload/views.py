from django.core.files.storage import default_storage
from django.http.response import FileResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from conventions.models import Convention
from programmes.models import Lot, Programme
from siap.siap_client.client import get_siap_credentials_from_request
from upload.models import UploadedFile, UploadedFileSerializer
from upload.services import UploadService
from upload.tasks import scan_uploaded_files


def _compute_dirpath(request):
    if "convention" in request.POST:
        convention = Convention.objects.get(uuid=request.POST["convention"])
        uuid = convention.uuid
        object_name = "conventions"
    elif "programme" in request.POST:
        programme = Programme.objects.get(uuid=request.POST["programme"])
        uuid = programme.uuid
        object_name = "programmes"
    elif "lot" in request.POST:
        lot = Lot.objects.get(uuid=request.POST["lot"])
        uuid = lot.uuid
        object_name = "lots"
    else:
        raise Exception(
            "/upload path should be called with a programme, lot or convention parameter"
        )
    return f"{object_name}/{uuid}/media/"


def _get_convention_uuid_from_request(request):
    if "convention" in request.POST:
        convention_uuid = request.POST["convention"]
    else:
        raise Exception("/upload path should be called with a convention parameter")
    return convention_uuid


@require_GET
def display_file(request, convention_uuid, uploaded_file_uuid):
    uploaded_file = UploadedFile.objects.get(uuid=uploaded_file_uuid)
    return FileResponse(
        default_storage.open(
            name=uploaded_file.filepath(convention_uuid),
            mode="rb",
        ),
        filename=uploaded_file.realname,
        as_attachment=True,
    )


@require_POST
def upload_file(request):
    files = request.FILES
    uploaded_files = []
    paths_to_scan = []
    dirpath = _compute_dirpath(request)

    for file in files.values():
        # compute path
        uploaded_file = UploadedFile.objects.create(
            filename=file.name,
            size=file.size,
            dirpath=dirpath,
            content_type=file.content_type,
        )

        upload_service = UploadService(
            convention_dirpath=uploaded_file.dirpath,
            filename=f"{uploaded_file.uuid}_{uploaded_file.filename}",
        )
        upload_service.upload_file(file)

        uploaded_file.save()
        paths_to_scan.append((upload_service.path, uploaded_file.pk))
        uploaded_files.append(UploadedFileSerializer(uploaded_file).data)

    scan_uploaded_files.delay(
        _get_convention_uuid_from_request(request),
        paths_to_scan,
        request.user.id,
        get_siap_credentials_from_request(request),
    )
    return JsonResponse({"success": "true", "uploaded_file": uploaded_files})
