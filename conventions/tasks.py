import logging
import os
from pathlib import Path
from typing import Any

from celery import chain, shared_task
from django.conf import settings
from django.core.files.storage import default_storage
from waffle import switch_is_active
from zipfile import ZipFile

from conventions.models import Convention, PieceJointe
from conventions.services.convention_generator import (
    PDFConversionError,
    generate_pdf,
    get_files_attached,
    get_or_generate_convention_doc,
    get_tmp_local_path,
)
from conventions.services.file import ConventionFileService
from core.services import EmailService, EmailTemplateID
from siap.siap_client.client import SIAPClient
from siap.siap_client.schemas import Alerte

logger = logging.getLogger(__name__)


@shared_task
def task_generate_and_send(
    convention_uuid: str,
    convention_url: str,
    convention_email_validator: str,
    siap_credentials: dict[str, Any],
):
    chain(
        task_generate_pdf.s(convention_uuid),
        task_send_email_to_bailleur.si(
            convention_uuid,
            convention_url,
            convention_email_validator,
            siap_credentials,
        ),
    )()


@shared_task(
    autoretry_for=(PDFConversionError,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=False,
)
def task_generate_pdf(convention_uuid: str) -> None:
    convention = Convention.objects.get(uuid=convention_uuid)
    doc = get_or_generate_convention_doc(convention=convention, save_data=True)
    generate_pdf(convention_uuid=convention_uuid, doc=doc)


@shared_task(
    retry_kwargs={"max_retries": 10},
    retry_backoff=True,
    retry_backoff_max=3600,
    retry_jitter=True,
)
def task_send_email_to_bailleur(  # noqa: C901
    convention_uuid: str,
    convention_url: str,
    convention_email_validator: str,
    siap_credentials: dict[str, Any],
) -> None:
    # Get the convention
    convention = Convention.objects.get(uuid=convention_uuid)

    # Get the bailleur emails
    destinataires_bailleur = convention.get_email_bailleur_users()
    if len(destinataires_bailleur) == 0:
        logger.error(f"No bailleur emails found for the convention {convention_uuid}")
        return

    # Get the administration
    administration = convention.administration
    if administration is None:
        logger.error(f"Missing administration for convention {convention_uuid}")
        return

    storage_path = Path("conventions", convention_uuid, "convention_docs")
    local_path = get_tmp_local_path()

    storage_pdf_path = storage_path / f"{convention_uuid}.pdf"
    if not default_storage.exists(storage_pdf_path):
        logger.error(f"Missing pdf file {storage_pdf_path}")
        return

    # Case 1 : need a zip with many files
    if not convention.is_avenant() and (
        convention.programme.is_foyer or convention.programme.is_residence
    ):
        local_pdf_path = local_path / f"convention_{convention.uuid}.pdf"
        local_zip_path = local_path / f"convention_{convention.uuid}.zip"

        storage_zip_path = storage_path / f"{convention.uuid}.zip"

        # Get the pdf file from storage and save it locally
        with default_storage.open(storage_pdf_path, "rb") as storage_pdf_file:
            with open(local_pdf_path, "wb") as local_pdf_file:
                local_pdf_file.write(storage_pdf_file.read())

        # Build the zip archive locally, with all the attached files
        with ZipFile(local_zip_path, "w") as local_zip_file:
            local_zip_file.write(str(local_pdf_path), arcname=(local_pdf_path).name)
            for p in get_files_attached(convention):
                local_zip_file.write(str(p), arcname=p.name)
                p.unlink()

        # Save the zip archive to the storage
        with open(local_zip_path, "rb") as local_zip_file:
            with default_storage.open(storage_zip_path, "wb") as storage_zip_file:
                storage_zip_file.write(local_zip_file.read())

        # Get rid of the local files
        if local_zip_path.exists():
            os.remove(local_zip_path)
        if local_pdf_path.exists():
            os.remove(local_pdf_path)

        email_file_path = storage_zip_path

    # Case 2 : we only need yo attach the pdf file
    else:
        email_file_path = storage_pdf_path

    # Check the size of the attached file
    if default_storage.size(email_file_path) > settings.MAX_EMAIL_ATTACHED_FILES_SIZE:
        logger.error(
            f"Email not sent for the convention {convention_uuid}: attached file is too big: {email_file_path}"
        )
        return

    if switch_is_active(settings.SWITCH_SIAP_ALERTS_ON):
        alerte = Alerte.from_convention(
            convention=convention,
            categorie_information="CATEGORIE_ALERTE_ACTION",
            destinataires=[
                # bailleurs ???
                # Destinataire(role="ADMINISTRATEUR", service="MO"),
                # Destinataire(role="ADMINISTRATEUR", service="SG"),
            ],
            etiquette="CUSTOM",
            etiquette_personnalisee=(
                "Avenant validé" if convention.is_avenant() else "Convention validée"
            ),
            type_alerte="Changement de statut",
            url_direction="/",
        )
        SIAPClient.get_instance().create_alerte(
            payload=alerte.to_json(),
            **siap_credentials,
        )

    if not switch_is_active(settings.SWITCH_TRANSACTIONAL_EMAILS_OFF):

        # Send a confirmation email to bailleurs
        EmailService(
            to_emails=destinataires_bailleur,
            cc_emails=[convention_email_validator],
            email_template_id=(
                EmailTemplateID.ItoB_AVENANT_VALIDE
                if convention.is_avenant()
                else EmailTemplateID.ItoB_CONVENTION_VALIDEE
            ),
        ).send_transactional_email(
            email_data={
                "convention_url": convention_url,
                "convention": str(convention),
                "adresse": administration.adresse,
                "code_postal": administration.code_postal,
                "ville": administration.ville,
                "nb_convention_exemplaires": administration.nb_convention_exemplaires,
            },
            filepath=email_file_path,
        )


@shared_task()
def promote_piece_jointe(pk: int):
    piece_jointe = PieceJointe.objects.get(id=pk)
    if piece_jointe.convention.nom_fichier_signe is None:
        ConventionFileService.promote_piece_jointe(piece_jointe)
