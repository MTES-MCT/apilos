import enum
import logging
import mimetypes
from pathlib import Path
from typing import List
from django.conf import settings

from django.core.mail import EmailMultiAlternatives
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

# Using enum class create enumerations
class EmailTemplateID(enum.Enum):
    # [PLATEFORME] BAILLEUR - Avenant à instruire - confirmation
    B_AVENANT_A_INSTRUIRE_CONFIRMATION = 106
    # [PLATEFORME] BAILLEUR - Convention à instruire - confirmation
    B_CONVENTION_A_INSTRUIRE_CONFIRMATION = 105
    # [PLATEFORME] BAILLEURS - Bienvenu sur la plateforme APiLos
    B_WELCOME = 84
    # [PLATEFORME] BAILLEUR à INSTRUCTEUR - Avenant à instruire
    BtoI_AVENANT_A_INSTRUIRE = 98
    # [PLATEFORME] BAILLEUR à INSTRUCTEUR - Convention à instruire
    BtoI_CONVENTION_A_INSTRUIRE = 97
    # [PLATEFORME] BAILLEUR à INSTRUCTEUR - Corrections faites - avenant à instruire à nouveau
    BtoI_AVENANT_CORRECTIONS_FAITES = 100
    # [PLATEFORME] BAILLEUR à INSTRUCTEUR - Corrections faites - convention à instruire à nouveau
    BtoI_CONVENTION_CORRECTIONS_FAITES = 99
    # [PLATEFORME] INSTRUCTEUR - Bienvenu sur la plateforme APiLos
    I_WELCOME = 96
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


class EmailService:
    subject: str
    from_email: str
    to_emails: List[str] | None
    cc_emails: List[str] | None
    text_content: str
    html_content: str
    email_template_id: EmailTemplateID

    def __init__(
        self,
        to_emails: List[str] | None = None,
        cc_emails: List[str] | None = None,
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
            if settings.SENDINBLUE_API_KEY:
                message.send()
            else:
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
