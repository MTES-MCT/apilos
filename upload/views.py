from django.http.response import JsonResponse, FileResponse
from django.views.decorators.http import require_POST, require_GET
from conventions.models import Convention
from programmes.models import Lot, Programme

from upload.services import UploadService
from upload.models import UploadedFile, UploadedFileSerializer


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


@require_GET
def display_file(request, convention_uuid, uploaded_file_uuid):
    uploaded_file = UploadedFile.objects.get(uuid=uploaded_file_uuid)
    file = UploadService().get_file(uploaded_file.filepath(convention_uuid))

    return FileResponse(
        file,
        filename=uploaded_file.filename,
        as_attachment=True,
    )


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

        upload_service = UploadService(
            convention_dirpath=uploaded_file.dirpath,
            filename=f"{uploaded_file.uuid}_{uploaded_file.filename}",
        )
        upload_service.upload_file(file)

        uploaded_file.save()
        uploaded_files.append(UploadedFileSerializer(uploaded_file).data)
    return JsonResponse({"success": "true", "uploaded_file": uploaded_files})
