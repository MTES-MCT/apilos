import dramatiq
from conventions.services import convention_generator, email as service_email
from conventions.models import Convention


@dramatiq.actor
def generate_and_send(args):
    convention_uuid = args["convention_uuid"]
    convention_recapitulatif_uri = args["convention_recapitulatif_uri"]
    convention_email_validator = args["convention_email_validator"]

    convention = Convention.objects.get(uuid=convention_uuid)

    file_stream = convention_generator.generate_convention_doc(convention, True)
    local_pdf_path = convention_generator.generate_pdf(file_stream, convention)

    service_email.send_email_valide(
        convention_recapitulatif_uri,
        convention,
        [convention_email_validator],
        local_pdf_path,
    )
