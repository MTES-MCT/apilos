import base64
import logging
import tempfile
from pathlib import Path
from typing import Any

import requests
from celery import shared_task
from django.conf import settings
from django.core.files.storage import default_storage
from waffle import switch_is_active

from conventions.models.convention import Convention
from conventions.services.alertes import ALERTE_CATEGORY_MAPPING
from core.services import EmailService, EmailTemplateID
from siap.siap_client.client import SIAPClient
from siap.siap_client.schemas import Alerte, Destinataire
from upload.models import UploadedFile
from users.models import User

logger = logging.getLogger(__name__)


def get_clamav_auth_header(username, password):
    creds = base64.b64encode(bytes(f"{username}:{password}", "utf-8"))
    return {"Authorization": b"Basic " + creds}


@shared_task()
def scan_uploaded_files(
    convention_uuid,
    paths_to_scan,
    authenticated_user_id,
    siap_credentials: dict[str, Any] | None = None,
):
    if not settings.CLAMAV_SERVICE_URL:
        return

    for path, uploaded_file_id in paths_to_scan:
        with default_storage.open(path) as original_file_object:
            file_is_infected = False
            with tempfile.NamedTemporaryFile() as tf:
                tf.write(original_file_object.read())
                tf.seek(0)
                headers = get_clamav_auth_header(
                    settings.CLAMAV_SERVICE_USER, settings.CLAMAV_SERVICE_PASSWORD
                )

                response = requests.post(
                    f"{settings.CLAMAV_SERVICE_URL}/v2/scan",
                    headers=headers,
                    timeout=120,
                    files={"file": tf},
                )

                data = response.json()
                file_is_infected = data["malware"]

            if file_is_infected:
                user = User.objects.get(id=authenticated_user_id)

                if (
                    switch_is_active(settings.SWITCH_SIAP_ALERTS_ON)
                    and siap_credentials
                ):
                    if not convention_uuid:
                        raise Exception(
                            "/upload should be called with a convention_uuid parameter"
                        )
                    convention = Convention.objects.get(uuid=convention_uuid)
                    alerte = Alerte.from_convention(
                        convention=convention,
                        categorie_information=ALERTE_CATEGORY_MAPPING["information"],
                        destinataires=[
                            Destinataire(role="INSTRUCTEUR", service="SG"),
                            Destinataire(role="INSTRUCTEUR", service="MO"),
                        ],
                        etiquette="CUSTOM",
                        etiquette_personnalisee=("Virus détecté sur un document"),
                        type_alerte="Détection de virus",
                        url_direction="/",
                    )
                    SIAPClient.get_instance().create_alerte(
                        payload=alerte.to_json(),
                        **siap_credentials,
                    )

                if not switch_is_active(settings.SWITCH_TRANSACTIONAL_EMAILS_OFF):
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
