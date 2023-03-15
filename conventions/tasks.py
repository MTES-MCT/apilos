from pathlib import Path
from zipfile import ZipFile

from celery import shared_task
from django.conf import settings
from django.core.files.storage import default_storage

from conventions.services.convention_generator import (
    generate_convention_doc,
    generate_pdf,
    get_files_attached,
)
from conventions.models import Convention, PieceJointe
from conventions.services.file import ConventionFileService
from core.services import EmailService, EmailTemplateID


@shared_task()
def generate_and_send(args):
    convention_uuid = args["convention_uuid"]
    convention_url = args["convention_url"]
    convention_email_validator = args["convention_email_validator"]

    convention = Convention.objects.get(uuid=convention_uuid)

    file_stream = generate_convention_doc(convention, True)
    pdf_path = generate_pdf(file_stream, convention)

    zip_path = None
    if not convention.is_avenant() and (
        convention.programme.is_foyer() or convention.programme.is_residence()
    ):
        zip_path = (
            Path("conventions")
            / str(convention.uuid)
            / "convention_docs"
            / f"convention_{convention.uuid}.zip"
        )
        local_zip_path = settings.MEDIA_ROOT / zip_path
        local_zip_path.parent.mkdir(parents=True, exist_ok=True)

        if settings.DEFAULT_FILE_STORAGE == "storages.backends.s3boto3.S3Boto3Storage":
            with default_storage.open(pdf_path, "rb") as src_file:
                with open(settings.MEDIA_ROOT / pdf_path, "wb") as desc_file:

                    desc_file.write(src_file.read())

        with ZipFile(local_zip_path, "w") as myzip:
            myzip.write(
                str(settings.MEDIA_ROOT / pdf_path),
                arcname=(settings.MEDIA_ROOT / pdf_path).name,
            )
            local_pathes = get_files_attached(convention)
            for local_path in local_pathes:
                myzip.write(
                    str(local_path),
                    arcname=local_path.name,
                )
                local_path.unlink()

        if settings.DEFAULT_FILE_STORAGE == "storages.backends.s3boto3.S3Boto3Storage":
            with open(local_zip_path, "rb") as src_file:
                with default_storage.open(zip_path, "wb") as desc_file:
                    desc_file.write(src_file.read())

    # Send a confirmation email to bailleur
    if len(destinataires_bailleur := convention.get_email_bailleur_users()) > 0:
        email_service_to_bailleur = EmailService(
            to_emails=destinataires_bailleur,
            cc_emails=[convention_email_validator],
            email_template_id=EmailTemplateID.ItoB_AVENANT_VALIDE
            if convention.is_avenant()
            else EmailTemplateID.ItoB_CONVENTION_VALIDEE,
        )
        administration = convention.administration

        file_path = zip_path if zip_path is not None else Path(pdf_path)
        if default_storage.size(file_path) > settings.MAX_EMAIL_ATTACHED_FILES_SIZE:
            file_path = None
        email_service_to_bailleur.send_transactional_email(
            email_data={
                "convention_url": convention_url,
                "convention": str(convention),
                "adresse": administration.adresse,
                "code_postal": administration.code_postal,
                "ville": administration.ville,
                "nb_convention_exemplaires": administration.nb_convention_exemplaires,
            },
            filepath=file_path,
        )


@shared_task()
def promote_piece_jointe(pk: int):
    piece_jointe = PieceJointe.objects.get(id=pk)
    if piece_jointe.convention.nom_fichier_signe is None:
        ConventionFileService.promote_piece_jointe(piece_jointe)
