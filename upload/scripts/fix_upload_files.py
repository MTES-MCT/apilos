# python manage.py shell < upload/scripts/fix_upload_files.py

import json
import re
from os.path import splitext
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models, transaction
from django.utils.text import slugify

from conventions.models import Convention
from upload.models import UploadedFile


def _load_uuids_from_log() -> list[dict[str, str]]:
    uuids = []

    log_filepath = Path(settings.BASE_DIR, "upload", "scripts", "s3-backup-errors.log")
    with open(log_filepath) as f:
        pattern = re.compile(
            r"apilos-prod/conventions/([0-9a-fA-F-]+)/media/([0-9a-fA-F-]+)"
        )
        for line in f.readlines():
            parts = pattern.findall(line)[0]
            assert len(parts) == 2, f"Expected 2 UUIDs, got {len(parts)}"
            uuids.append(
                {
                    "convention_uuid": parts[0],
                    "upload_file_uuid": parts[1],
                }
            )

    return uuids


def _get_conv_upload_fields() -> list[str]:
    return [
        field.name
        for field in Convention._meta.get_fields()
        if isinstance(field, models.TextField)
    ]


def handle_conv_upload(convention_uuid: str, upload_file_uuid: str):
    convention = Convention.objects.filter(uuid=convention_uuid).first()
    assert convention is not None, f"Convention {convention_uuid} not found"

    uploaded_file = UploadedFile.objects.filter(uuid=upload_file_uuid).first()
    assert uploaded_file is not None, f"UploadedFile {upload_file_uuid} not found"

    for field_name in _get_conv_upload_fields():
        if not (field_value := getattr(convention, field_name)):
            continue
        try:
            json_field_value = json.loads(field_value)
        except json.JSONDecodeError:
            continue
        if upload_file_uuid not in json_field_value["files"]:
            continue

        # get the current upload data
        upload_filepath = uploaded_file.filepath(convention_uuid)
        upload_content = default_storage.open(
            uploaded_file.filepath(convention_uuid), "rb"
        )

        # compute the new file name
        name, extension = splitext(
            json_field_value["files"][upload_file_uuid]["filename"]
        )
        new_filename = f"{slugify(name)}{extension}"

        with transaction.atomic():
            # update the convention field value
            json_field_value["files"][upload_file_uuid]["filename"] = new_filename
            setattr(convention, field_name, json.dumps(json_field_value))
            convention.save()

            # update the upload file name
            uploaded_file.filename = new_filename
            uploaded_file.save()

        # save the new file on S3
        new_upload_filepath = uploaded_file.filepath(convention_uuid)
        default_storage.save(name=new_upload_filepath, content=upload_content)

        # delete the previous file on S3
        default_storage.delete(upload_filepath)


def main():
    for uuids in _load_uuids_from_log():
        handle_conv_upload(
            convention_uuid=uuids["convention_uuid"],
            upload_file_uuid=uuids["upload_file_uuid"],
        )


main()
