from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from upload.services import UploadService


def send_email_valide(convention_url, convention, cc, local_pdf_path=None):

    if local_pdf_path is not None:
        extention = local_pdf_path.split(".")[-1]

    from_email = "contact@apilos.beta.gouv.fr"

    # All bailleur users from convention
    to = convention.get_email_bailleur_users()

    text_content = render_to_string(
        "emails/bailleur_valide.txt",
        {
            "convention_url": convention_url,
            "convention": convention,
            "administration": convention.programme.administration,
        },
    )
    html_content = render_to_string(
        "emails/bailleur_valide.html",
        {
            "convention_url": convention_url,
            "convention": convention,
            "administration": convention.programme.administration,
        },
    )

    if to:
        msg = EmailMultiAlternatives(
            f"Convention validé ({convention})", text_content, from_email, to, cc=cc
        )
        msg.attach_alternative(html_content, "text/html")

        if local_pdf_path is not None:
            pdf_file_handler = UploadService().get_file(local_pdf_path)
            if extention == "pdf":
                msg.attach(
                    f"{convention}.pdf", pdf_file_handler.read(), "application/pdf"
                )
            if extention == "docx":
                msg.attach(
                    f"{convention}.docx",
                    pdf_file_handler.read(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingm",
                )
            pdf_file_handler.close()
            msg.content_subtype = "html"

        msg.send()
    else:
        msg = EmailMultiAlternatives(
            f"[ATTENTION pas de destinataire à cet email] Convention validé ({convention})",
            text_content,
            from_email,
            ("contact@apilos.beta.gouv.fr",),
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    return msg
