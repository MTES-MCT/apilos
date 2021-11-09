import json
from enum import Enum
from upload.models import UploadedFile


def format_date_for_form(date):
    return date.strftime("%Y-%m-%d") if date is not None else ""


class ReturnStatus(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    WARNING = "WARNING"


def set_files_and_text_field(files_field, text_field=""):
    files = []
    if files_field and isinstance(files_field, str):
        files = json.loads(files_field.replace("'", '"'))
    field = {"files": files, "text": text_field}
    return json.dumps(field)


def get_text_and_files_from_field(name, field):
    object_field = {}

    files = {}
    if field:
        try:
            object_field = json.loads(field)
        except json.decoder.JSONDecodeError:
            object_field = {
                "files": {},
                "text": field if isinstance(field, str) else "",
            }
        files = object_field["files"]

    returned_files = {}
    for file in UploadedFile.objects.filter(uuid__in=files):
        returned_files[str(file.uuid)] = {
            "uuid": str(file.uuid),
            "filename": file.filename,
            "size": file.size,
            "content_type": file.content_type,
            "thumbnail": files[str(file.uuid)]["thumbnail"]
            if "thumbnail" in files[str(file.uuid)]
            else None,
        }
    object_field["files"] = json.dumps(returned_files)
    return {
        name: object_field["text"] if "text" in object_field else "",
        name + "_files": object_field["files"],
    }


def base_convention_response_error(
    request, convention, perm="convention.change_convention"
):
    return {
        "success": ReturnStatus.ERROR,
        "convention": convention,
        "comments": convention.get_comments_dict(),
        "editable": request.user.has_perm(perm, convention),
    }
