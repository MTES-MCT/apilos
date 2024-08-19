import enum
import logging
import mimetypes
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


# Using enum class create enumerations
# These numeric ids match campaign templates ids.
# They are listed under Brevo dashboard> Campaigns > Templates
class EmailTemplateID(enum.Enum):
    # [PLATEFORME] BAILLEUR - Avenant à instruire - confirmation
    B_AVENANT_A_INSTRUIRE_CONFIRMATION = 106
    # [PLATEFORME] BAILLEUR - Convention à instruire - confirmation
    B_CONVENTION_A_INSTRUIRE_CONFIRMATION = 105
    # [PLATEFORME] BAILLEUR à INSTRUCTEUR - Avenant à instruire
    BtoI_AVENANT_A_INSTRUIRE = 167
    # [PLATEFORME] BAILLEUR à INSTRUCTEUR - Convention à instruire
    BtoI_CONVENTION_A_INSTRUIRE = 166
    # [PLATEFORME] BAILLEUR à INSTRUCTEUR - Corrections faites - avenant à instruire à nouveau
    BtoI_AVENANT_CORRECTIONS_FAITES = 169
    # [PLATEFORME] BAILLEUR à INSTRUCTEUR - Corrections faites - convention à instruire à nouveau
    BtoI_CONVENTION_CORRECTIONS_FAITES = 168
    # [PLATEFORME] INSTRUCTEUR à BAILLEUR - Avenant validé
    ItoB_AVENANT_VALIDE = 104
    # [PLATEFORME] INSTRUCTEUR à BAILLEUR - Convention validée
    ItoB_CONVENTION_VALIDEE = 103
    # [PLATEFORME] INSTRUCTEUR à BAILLEUR - Corrections requises - avenant à corriger
    ItoB_AVENANT_CORRECTIONS_REQUISES = 101
    # [PLATEFORME] INSTRUCTEUR à BAILLEUR - Corrections requises - convention à corriger
    ItoB_CONVENTION_CORRECTIONS_REQUISES = 102
    # [PLATEFORME] Bailleurs - 2 - RETENTION (Questionnaire de satisfaction)
    B_SATISFACTION = 138
    # [PLATEFORME] Instructeurs - 2 - RETENTION (Questionnaire de satisfaction)
    I_SATISFACTION = 139
    # Instructeurs - 5 - ACTIVATION (récapitulatif mensuel)
    I_MENSUEL = 151
    # Bailleurs - 5 - ACTIVATION (récapitulatif mensuel)
    B_MENSUEL = 152
    # Virus - 163 - Warning
    VIRUS_WARNING = 163


class EmailService:
    subject: str
    from_email: str
    to_emails: list[str] | None
    cc_emails: list[str] | None
    text_content: str
    html_content: str
    email_template_id: EmailTemplateID

    def __init__(
        self,
        to_emails: list[str] | None = None,
        cc_emails: list[str] | None = None,
        email_template_id: EmailTemplateID = None,
    ):
        self.to_emails = to_emails
        self.cc_emails = cc_emails
        self.email_template_id = email_template_id

    def send_transactional_email(
        self, *, email_data: dict | None = None, filepath: Path | None = None
    ):
        if not self.email_template_id:
            raise Exception("missing email_template_id")

        if not self.to_emails:
            logger.warning("No recipient for email")
        else:
            message = EmailMultiAlternatives(
                to=self.to_emails,
                cc=self.cc_emails,
            )
            message.template_id = self.email_template_id.value
            message.from_email = None  # to use the template's default sender
            if email_data:
                message.merge_global_data = email_data
            if filepath:
                with default_storage.open(filepath, "rb") as f:
                    (content_type, _) = mimetypes.guess_type(filepath.name)
                    message.attach(
                        filepath.name,
                        f.read(),
                        content_type,
                    )
            if settings.DEBUG:
                logger.warning(
                    """
                    Email message:
                        to: %s
                        cc: %s
                        template_id: %s
                        data: %s
                    """,
                    message.to,
                    message.cc,
                    message.template_id,
                    message.merge_global_data,
                )

            message.send()
