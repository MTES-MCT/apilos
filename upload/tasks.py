import logging
import subprocess
from pathlib import Path

from celery import shared_task
from django.conf import settings

from core.services import EmailService, EmailTemplateID
from upload.models import UploadedFile
from users.models import User

logger = logging.getLogger(__name__)


@shared_task()
def scan_uploaded_files(paths_to_scan, authenticated_user_id):
    if "CLAMAV_PATH" not in settings:
        return

    # refresh the database on demand before the scan starts
    subprocess.run(
        f'freshclam --config-file="{settings.CLAMAV_PATH}/clamav/freshclam.conf"',
        shell=True,
        check=True,
    )

    for path, uploaded_file_id in paths_to_scan:
        path = Path(settings.MEDIA_ROOT / path).resolve()
        output = subprocess.run(
            f'clamdscan {path} --config-file="{settings.CLAMAV_PATH}/clamav/clamd.conf"',
            capture_output=True,
            text=True,
            check=False,
        )

        if (
            "Infected files" in output.stdout
            and "Infected files: 0" not in output.stdout
        ):
            user = User.objects.get(id=authenticated_user_id)
            EmailService(
                to_emails=[user.email],
                email_template_id=EmailTemplateID.VIRUS_WARNING,
            ).send_transactional_email(
                email_data={
                    "firstname": user.first_name,
                    "lastname": user.last_name,
                    "filename": path.name,
                }
            )
            path.unlink()
            UploadedFile.objects.get(id=uploaded_file_id).delete()

            logger.warning(
                "An infected file has been detected."
                "The user has been warned by email "
                "and the file has succesfully been removed. | File location : %s",
                path,
            )
