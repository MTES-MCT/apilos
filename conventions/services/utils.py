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


def init_text_and_files_from_field(request, object_instance, field_name):
    if (
        request.POST.get(field_name + "_files") is not None
        or request.POST.get(field_name) is not None
    ):
        form_fields = {}
        form_fields[field_name] = request.POST.get(field_name)
        form_fields[field_name + "_files"] = request.POST.get(field_name + "_files")
        return form_fields
    return get_text_and_files_from_field(
        field_name, getattr(object_instance, field_name)
    )


def get_form_value(form_instance, object_instance, field_name):
    if form_instance[field_name].value() is not None:
        return form_instance[field_name].value()
    return getattr(object_instance, field_name)


def build_partial_form(request, convention_object, field_list):
    fields_dict = {}
    for field in field_list:
        fields_dict[field] = request.POST.get(field, getattr(convention_object, field))
    return fields_dict


def build_partial_text_and_files_form(request, convention_object, field_list):
    fields_dict = {}
    for field in field_list:
        fields_dict = {
            **fields_dict,
            **init_text_and_files_from_field(request, convention_object, field),
        }
    return fields_dict


def base_convention_response_error(request, convention):
    return {
        "success": ReturnStatus.ERROR,
        "convention": convention,
        "comments": convention.get_comments_dict(),
        "editable": request.user.full_editable_convention(convention),
    }


def base_response_success(convention):
    return {
        "success": ReturnStatus.SUCCESS,
        "convention": convention,
    }


def base_response_redirect_recap_success(convention):
    return {
        "success": ReturnStatus.SUCCESS,
        "convention": convention,
        "redirect": "recapitulatif",
    }
