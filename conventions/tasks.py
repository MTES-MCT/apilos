from pathlib import Path
from zipfile import ZipFile

import dramatiq
from django.conf import settings
from django.core.files.storage import default_storage

from conventions.services import convention_generator
from conventions.models import Convention, PieceJointe
from conventions.services.file import ConventionFileService
from core.services import EmailService, EmailTemplateID


@dramatiq.actor
def generate_and_send(args):
    convention_uuid = args["convention_uuid"]
    convention_url = args["convention_url"]
    convention_email_validator = args["convention_email_validator"]

    convention = Convention.objects.get(uuid=convention_uuid)

    file_stream = convention_generator.generate_convention_doc(convention, True)
    pdf_path = convention_generator.generate_pdf(file_stream, convention)

    zip_path = None
    if convention.programme.is_foyer():
        zip_path = (
            Path("conventions")
            / str(convention.uuid)
            / "convention_docs"
            / f"convention_{convention.uuid}.zip"
        )
        local_zip_path = settings.MEDIA_ROOT / zip_path
        if settings.DEFAULT_FILE_STORAGE == "storages.backends.s3boto3.S3Boto3Storage":
            with default_storage.open(pdf_path, "rb") as src_file:
                with open(settings.MEDIA_ROOT / pdf_path, "wb") as desc_file:

                    desc_file.write(src_file.read())

        with ZipFile(local_zip_path, "w") as myzip:
            myzip.write(
                str(settings.MEDIA_ROOT / pdf_path),
                arcname=(settings.MEDIA_ROOT / pdf_path).name,
            )
            local_pathes = convention_generator.get_files_attached(convention)
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

    if settings.SENDINBLUE_API_KEY:
        # Send a confirmation email to bailleur
        email_service_to_bailleur = EmailService(
            to_emails=convention.get_email_bailleur_users(),
            email_template_id=EmailTemplateID.ItoB_AVENANT_VALIDE
            if convention.is_avenant()
            else EmailTemplateID.ItoB_CONVENTION_VALIDEE,
        )
        administration = convention.administration

        file_path = zip_path if zip_path is not None else Path(pdf_path)
        if default_storage.size(file_path) > 10000000:

            file_path = None
        # TODO test the if the size of file to attached if greater than 10 Mo
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
    else:

        EmailService().send_email_valide(
            convention_url,
            convention,
            convention.get_email_bailleur_users(),
            [convention_email_validator],
            str(zip_path) if zip_path is not None else str(pdf_path),
        )


@dramatiq.actor
def promote_piece_jointe(pk: int):
    piece_jointe = PieceJointe.objects.get(id=pk)
    if piece_jointe.convention.nom_fichier_signe is None:
        ConventionFileService.promote_piece_jointe(piece_jointe)
