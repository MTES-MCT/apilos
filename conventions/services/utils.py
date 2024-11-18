import json
from datetime import datetime
from enum import Enum

from django.http import HttpRequest

from conventions.models import Convention, ConventionStatut
from conventions.templatetags.custom_filters import is_bailleur, is_instructeur
from core.utils import is_valid_uuid
from upload.models import UploadedFile


def format_date_for_form(date):
    return date.strftime("%Y-%m-%d") if date is not None else ""


class ReturnStatus(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    WARNING = "WARNING"
    # used to manage success without redirect on next step on step form
    REFRESH = "REFRESH"


def set_files_and_text_field(files_field, text_field=""):
    files = []
    if files_field and files_field != "None" and isinstance(files_field, str):
        files = json.loads(files_field)
    field = {"files": files, "text": text_field}
    return json.dumps(field)


def get_text_and_files_from_field(name, field):
    object_field = {}

    files = {}
    if field:
        try:
            object_field = json.loads(field)
            # Fix potentially malformed JSON
            if not isinstance(object_field["files"], dict):
                object_field["files"] = {}
        except json.decoder.JSONDecodeError:
            object_field = {
                "files": {},
                "text": field if isinstance(field, str) else "",
            }
        files = {
            k: v
            for k, v in object_field.get("files", files).items()
            if is_valid_uuid(k)
        }
    returned_files = {}
    for file in UploadedFile.objects.filter(uuid__in=files):
        returned_files[str(file.uuid)] = {
            "uuid": str(file.uuid),
            "filename": file.filename,
            "realname": file.realname,
            "size": file.size,
            "content_type": file.content_type,
            "thumbnail": (
                files[str(file.uuid)]["thumbnail"]
                if "thumbnail" in files[str(file.uuid)]
                else None
            ),
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


def get_form_date_value(form_instance, object_instance, field_name):
    if form_instance[field_name].value() is not None:
        return form_instance[field_name].value()
    return format_date_for_form(
        getattr(object_instance, field_name)
    )  # format_date_for_form(


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
        "editable": editable_convention(request, convention),
    }


def editable_convention(request: HttpRequest, convention: Convention):
    if "readonly" in request.session and request.session["readonly"]:
        return False
    if is_instructeur(request):
        if "is_expert" in request.session and request.session["is_expert"] is True:
            return True
        return convention.statut in [
            ConventionStatut.PROJET.label,
            ConventionStatut.INSTRUCTION.label,
            ConventionStatut.CORRECTION.label,
        ]
    if is_bailleur(request):
        return convention.statut == ConventionStatut.PROJET.label
    return False


def set_from_form_or_object(field, form, obj):
    setattr(
        obj,
        field,
        (
            form.cleaned_data[field]
            if form.cleaned_data[field] is not None
            else getattr(obj, field)
        ),
    )


def convention_upload_filename(convention: Convention) -> str:

    def _normalize(numero: str | None) -> str | None:
        if numero:
            return numero.replace(" ", "_")

    parts = []

    if convention.parent:
        parts += [
            f"convention_{_normalize(convention.parent.numero)}",
            f"avenant_{_normalize(convention.numero) or 'N'}",
        ]
    else:
        parts += [
            f"convention_{_normalize(convention.numero) or 'NUM'}",
        ]

    if convention.statut == ConventionStatut.PROJET.label:
        parts.append("projet")

    parts.append(datetime.now().strftime("%Y-%m-%d_%H-%M"))

    return f"{'_'.join(parts)}.pdf"
