from typing import List
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from conventions.models import Convention

from upload.services import UploadService


class EmailService:
    subject: str
    from_email: str
    to_emails: List[str] | None
    text_content: str
    html_content: str
    attachements: List

    def __init__(
        self,
        subject: str = "",
        to_emails: List[str] | None = None,
        cc_emails: List[str] | None = None,
        text_content: str = "",
        html_content: str = "",
        from_email: str = "contact@apilos.beta.gouv.fr",
    ):
        self.subject = subject
        self.to_emails = to_emails
        self.cc_emails = cc_emails
        self.text_content = text_content
        self.html_content = html_content
        self.from_email = from_email
        self.msg = None

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

        self.text_content = render_to_string(
            "emails/bailleur_valide.txt",
            {
                "convention_url": convention_url,
                "convention": convention,
                "administration": convention.programme.administration,
            },
        )
        self.html_content = render_to_string(
            "emails/bailleur_valide.html",
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
            pdf_file_handler.close()
            self.msg.content_subtype = "html"

        self.msg.send()
