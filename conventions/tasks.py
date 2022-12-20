from zipfile import ZipFile
from django.conf import settings
import dramatiq
from conventions.services import convention_generator
from conventions.models import Convention
from core.services import EmailService


@dramatiq.actor
def generate_and_send(args):
    convention_uuid = args["convention_uuid"]
    convention_recapitulatif_uri = args["convention_recapitulatif_uri"]
    convention_email_validator = args["convention_email_validator"]

    convention = Convention.objects.get(uuid=convention_uuid)

    file_stream = convention_generator.generate_convention_doc(convention, True)
    local_pdf_path = convention_generator.generate_pdf(file_stream, convention)

    if convention.programme.is_foyer():
        local_zip_path = (
            settings.MEDIA_ROOT
            / "conventions"
            / str(convention.uuid)
            / "convention_docs"
            / f"convention_{convention.uuid}.zip"
        )
        with ZipFile(local_zip_path, "w") as myzip:
            myzip.write(
                str(settings.MEDIA_ROOT / local_pdf_path),
                arcname=(settings.MEDIA_ROOT / local_pdf_path).name,
            )
            local_pathes = convention_generator.get_files_attached(convention)
            for local_path in local_pathes:
                myzip.write(
                    str(local_path),
                    arcname=local_path.name,
                )
                local_path.unlink()

    EmailService().send_email_valide(
        convention_recapitulatif_uri,
        convention,
        convention.get_email_bailleur_users(),
        [convention_email_validator],
        str(local_zip_path) if local_zip_path is not None else str(local_pdf_path),
    )
