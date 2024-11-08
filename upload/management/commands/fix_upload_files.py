import json
import re
from collections.abc import Generator
from os.path import splitext
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import models, transaction
from django.utils.text import slugify

from conventions.models import Convention
from upload.models import UploadedFile


class Command(BaseCommand):
    def handle(self, *args, **options):
        for uuids in self._load_uuids_from_log():
            self._handle_conv_upload(
                convention_uuid=uuids["convention_uuid"],
                upload_file_uuid=uuids["upload_file_uuid"],
            )

    def _load_uuids_from_log(self) -> Generator[dict[str, str]]:
        log_filepath = Path(
            settings.BASE_DIR,
            "upload",
            "management",
            "commands",
            "s3-backup-errors.log",
        )
        self.stdout.write(f"Reading log file {log_filepath}")

        pattern = re.compile(
            r"apilos-prod/conventions/([0-9a-fA-F-]+)/media/([0-9a-fA-F-]+)"
        )

        with open(log_filepath) as f:
            for line in f.readlines():
                parts = pattern.findall(line)[0]
                if not len(parts) == 2:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to parse line, expected 2 UUIDs, got {len(parts)}"
                        )
                    )
                    continue

                yield {
                    "convention_uuid": parts[0],
                    "upload_file_uuid": parts[1],
                }

    def _get_conv_upload_fields(self) -> list[str]:
        return [
            field.name
            for field in Convention._meta.get_fields()
            if isinstance(field, models.TextField)
        ]

    def _handle_conv_upload(self, convention_uuid: str, upload_file_uuid: str):
        convention = Convention.objects.filter(uuid=convention_uuid).first()
        if convention is None:
            self.stdout.write(
                self.style.ERROR(f"Convention {convention_uuid} not found")
            )
            return

        uploaded_file = UploadedFile.objects.filter(uuid=upload_file_uuid).first()
        if uploaded_file is None:
            self.stdout.write(
                self.style.ERROR(f"UploadedFile {upload_file_uuid} not found")
            )
            return

        self.stdout.write(
            f"Processing upload {upload_file_uuid} on convention {convention_uuid}."
        )

        for field_name in self._get_conv_upload_fields():
            if not (field_value := getattr(convention, field_name)):
                continue

            # check if the field content is a valid JSON content
            try:
                json_field_value = json.loads(field_value)
            except json.JSONDecodeError:
                continue

            # check if the upload file is correctly referenced in the JSON field content,
            # and if a filename is present
            if upload_file_uuid not in json_field_value["files"]:
                continue
            if "filename" not in json_field_value["files"][upload_file_uuid]:
                self.stdout.write(
                    self.style.ERROR(
                        f"Upload {upload_file_uuid} on convention {convention_uuid} has no filename"
                    )
                )
                continue

            # check the current file exists on S3
            previous_upload_filepath = uploaded_file.filepath(convention_uuid)
            if not default_storage.exists(previous_upload_filepath):
                self.stdout.write(
                    self.style.ERROR(
                        f"Upload {upload_file_uuid} on convention {convention_uuid} not found on S3"
                    )
                )
                continue

            # fetch the current upload data
            upload_content = default_storage.open(previous_upload_filepath, "rb")

            # compute the new file name
            name, extension = splitext(
                json_field_value["files"][upload_file_uuid]["filename"]
            )
            new_filename = f"{slugify(name)}{extension}"
            self.stdout.write(
                f"Changing {json_field_value['files'][upload_file_uuid]['filename']} to {new_filename}"
            )

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
            default_storage.delete(previous_upload_filepath)
