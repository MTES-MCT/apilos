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

    EmailService().send_email_valide(
        convention_recapitulatif_uri,
        convention,
        convention.get_email_bailleur_users(),
        [convention_email_validator],
        local_pdf_path,
    )
