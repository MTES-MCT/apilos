import uuid

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from conventions.models.choices import ConventionStatut
from core.services import EmailService, EmailTemplateID


class ConventionHistory(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    convention = models.ForeignKey(
        "Convention",
        on_delete=models.CASCADE,
        null=False,
        related_name="conventionhistories",
    )
    statut_convention = models.CharField(
        max_length=25,
        choices=ConventionStatut.choices,
        default=ConventionStatut.PROJET,
    )
    statut_convention_precedent = models.CharField(
        max_length=25,
        choices=ConventionStatut.choices,
        default=ConventionStatut.PROJET,
    )
    commentaire = models.TextField(null=True, blank=True)
    user = models.ForeignKey(
        "users.User",
        related_name="valide_par",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)


# pylint: disable=W0613
@receiver(post_save, sender=ConventionHistory)
def send_survey_email(sender, instance, *args, **kwargs):
    # send email to get user satisfaction after instructeur validate convention
    # or bailleur submit convention for the first time ?

    # check if it is the first time the bailleur user submit a convention
    if (
        instance.statut_convention == ConventionStatut.INSTRUCTION
        and not ConventionHistory.objects.filter(
            user=instance.user, statut_convention=ConventionStatut.INSTRUCTION
        ).exclude(id=instance.id)
        and instance.user.is_bailleur()
    ):
        EmailService(
            to_emails=[instance.user.email],
            email_template_id=EmailTemplateID.B_SATISFACTION,
        ).send_transactional_email(
            email_data={
                "email": instance.user.email,
                "firstname": instance.user.first_name,
                "lastname": instance.user.last_name,
            }
        )

    # check if it is the first time the instructeur user validate a convention
    if (
        instance.statut_convention == ConventionStatut.A_SIGNER
        and not ConventionHistory.objects.filter(
            user=instance.user, statut_convention=ConventionStatut.A_SIGNER
        ).exclude(id=instance.id)
        and instance.user.is_instructeur()
    ):
        EmailService(
            to_emails=[instance.user.email],
            email_template_id=EmailTemplateID.I_SATISFACTION,
        ).send_transactional_email(
            email_data={
                "email": instance.user.email,
                "firstname": instance.user.first_name,
                "lastname": instance.user.last_name,
            }
        )
