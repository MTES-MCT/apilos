import enum
import mimetypes
from pathlib import Path
from typing import List
from django.conf import settings

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.files.storage import default_storage

from conventions.models import Convention
from upload.services import UploadService

# Using enum class create enumerations
class EmailTemplateID(enum.Enum):
    # [PLATEFORME] BAILLEUR - Avenant à instruire - confirmation
    B_AVENANT_A_INSTRUIRE = 106
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


class EmailService:
    subject: str
    from_email: str
    to_emails: List[str] | None
    text_content: str
    html_content: str
    attachements: List
    email_template_id: EmailTemplateID

    def __init__(
        self,
        subject: str = "",
        to_emails: List[str] | None = None,
        cc_emails: List[str] | None = None,
        text_content: str = "",
        html_content: str = "",
        from_email: str = settings.DEFAULT_FROM_EMAIL,
        email_template_id: EmailTemplateID = None,
    ):
        self.to_emails = to_emails
        self.cc_emails = cc_emails
        self.email_template_id = email_template_id

        self.subject = subject
        self.text_content = text_content
        self.html_content = html_content
        self.from_email = from_email
        self.msg = None

    def send_transactional_email(self, email_data={}, filepath: Path | None = None):
        if not settings.SENDINBLUE_API_KEY or not self.email_template_id:
            return

        message = EmailMultiAlternatives(
            to=self.to_emails,
            cc=self.cc_emails,
        )
        message.template_id = self.email_template_id
        message.from_email = None  # to use the template's default sender
        message.merge_global_data = email_data
        # {
        #     "email": "toto@email.org",
        #     "username": "toto",
        #     "password": "Toto@Password",
        #     "firstname": "Toto",
        #     "lastname": "Oudard",
        #     "login_url": "https://apilos.beta.gouv.fr/login",
        # }
        if filepath:
            f = default_storage.open(filepath, "rb")
            message.attach(
                filepath.name,
                f.read(),
                mimetypes.guess_type(filepath.name),
                # "application/vnd.openxmlformats-officedocument.wordprocessingm",
            )
            f.close()
        message.send()

    def build_msg(self) -> None:
        if not self.to_emails:
            self.subject = "[ATTENTION pas de destinataire à cet email] " + self.subject
            self.to_emails = ["contact@apilos.beta.gouv.fr"]
            self.cc_emails = []
        self.msg = EmailMultiAlternatives(
            self.subject,
            self.text_content,
            self.from_email,
            self.to_emails,
            cc=self.cc_emails,
        )
        self.msg.attach_alternative(self.html_content, "text/html")

    def send(self) -> None:
        self.build_msg()
        self.msg.send()

    def send_to_devs(self) -> None:
        self.to_emails = ["dev@apilos.beta.gouv.fr"]
        self.build_msg()
        self.msg.send()

    def send_welcome_email(self, user, password, login_url) -> None:
        # envoi au bailleur
        if not user.is_bailleur():
            login_url = login_url + "?instructeur=1"

        # All bailleur users from convention
        self.to_emails = [user.email]
        self.text_content = render_to_string(
            "emails/welcome_user.txt",
            {"password": password, "user": user, "login_url": login_url},
        )
        self.html_content = render_to_string(
            "emails/welcome_user.html",
            {"password": password, "user": user, "login_url": login_url},
        )
        self.subject = "Bienvenue sur la plateforme APiLos"
        self.build_msg()
        self.msg.send()

    def send_email_valide(
        self,
        convention_url: str,
        convention: Convention,
        to: List,
        cc: List,
        local_pdf_path: str | None = None,
    ) -> None:

        self.subject = f"Convention validée ({convention})"
        self.to_emails = to
        self.cc_emails = cc

        if convention.is_avenant():
            template_label = "avenants/ItoB_validated_convention"
        else:
            template_label = "conventions/ItoB_validated_convention"

        self.text_content = render_to_string(
            f"emails/{template_label}.txt",
            {
                "convention_url": convention_url,
                "convention": convention,
                "administration": convention.programme.administration,
            },
        )
        self.html_content = render_to_string(
            f"emails/{template_label}.html",
            {
                "convention_url": convention_url,
                "convention": convention,
                "administration": convention.programme.administration,
            },
        )

        self.build_msg()
        if to and local_pdf_path is not None:
            extention = local_pdf_path.split(".")[-1]
            pdf_file_handler = UploadService().get_file(local_pdf_path)
            if extention == "pdf":
                self.msg.attach(
                    f"{convention}.pdf", pdf_file_handler.read(), "application/pdf"
                )
            if extention == "docx":
                self.msg.attach(
                    f"{convention}.docx",
                    pdf_file_handler.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingm",
                )
            if extention == "zip":
                self.msg.attach(
                    f"{convention}.zip", pdf_file_handler.read(), "application/zip"
                )
            pdf_file_handler.close()
            self.msg.content_subtype = "html"

        self.msg.send()
