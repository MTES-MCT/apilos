import base64
import logging
import tempfile
from pathlib import Path

import requests
from celery import shared_task
from django.conf import settings
from django.core.files.storage import default_storage

from core.services import EmailService, EmailTemplateID
from upload.models import UploadedFile
from users.models import User

logger = logging.getLogger(__name__)


def _get_auth_header(username, password):
    creds = base64.b64encode(bytes("{}:{}".format(username, password), "utf-8"))
    return dict(Authorization=b"Basic " + creds)


@shared_task()
def scan_uploaded_files(paths_to_scan, authenticated_user_id):
    if not settings.CLAMAV_SERVICE_URL:
        return

    for path, uploaded_file_id in paths_to_scan:
        with default_storage.open(path) as original_file_object:
            file_is_infected = False
            with tempfile.NamedTemporaryFile() as tf:
                tf.write(original_file_object.read())
                tf.seek(0)
                headers = {
                    **_get_auth_header(
                        settings.CLAMAV_SERVICE_USER, settings.CLAMAV_SERVICE_PASSWORD
                    ),
                    "Transfer-encoding": "chunked",
                }

                response = requests.post(
                    f"{settings.CLAMAV_SERVICE_URL}/v2/scan-chunked",
                    headers=headers,
                    data=tf,
                    timeout=120,
                )
                logger.warning(response)

                file_is_infected = True

            if file_is_infected:
                user = User.objects.get(id=authenticated_user_id)
                EmailService(
                    to_emails=[user.email],
                    email_template_id=EmailTemplateID.VIRUS_WARNING,
                ).send_transactional_email(
                    email_data={
                        "firstname": user.first_name,
                        "lastname": user.last_name,
                        "filename": Path(path).name,
                    }
                )

                default_storage.delete(path)
                UploadedFile.objects.get(id=uploaded_file_id).delete()

                logger.warning(
                    "An infected file has been detected."
                    "The user has been warned by email "
                    "and the file has succesfully been removed. | File location : %s",
                    path,
                )
