from django.conf import settings
from django.db.models import Q
from django.urls import reverse

from conventions.models import Convention
from core.services import EmailService, EmailTemplateID
from users.models import User


class UserService:
    @classmethod
    def extract_username_from_email(cls, email: str | None = None):
        if email is None:
            return ""

        parts = email.split("@", maxsplit=1)

        if len(parts) > 1:
            return parts[0].lower()

        return ""

    @classmethod
    def email_mensuel(cls) -> dict:
        nb_sent_emails = {
            "bailleur": 0,
            "instructeur": 0,
        }
        # liste des instructeurs concernés par le mail
        # ceuxi qui ont coché la case "tous"
        instructeur_tous_mails = Q(
            roles__typologie="INSTRUCTEUR",
            preferences_email="TOUS",
            roles__administration__programme__conventions__statut__in=[
                "2. Instruction requise",
                "4. A signer",
            ],
        )
        # "partiel" : au moins une convention en instruction dans l'administration
        instructeur_partiel_instruction = Q(
            roles__typologie="INSTRUCTEUR",
            preferences_email="PARTIEL",
            roles__administration__programme__conventions__statut="2. Instruction requise",
        )
        # "partiel" : les instructeurs ayant validé au moins une convention en isntruction
        instructeur_partiel_signature = Q(
            roles__typologie="INSTRUCTEUR",
            preferences_email="PARTIEL",
            valide_par__convention__statut="4. A signer",
        )
        for instructeur in (
            User.objects.filter(cerbere_login__isnull=True)
            .filter(
                instructeur_tous_mails
                | instructeur_partiel_instruction
                | instructeur_partiel_signature
            )
            .distinct()
        ):
            if instructeur.preferences_email == "PARTIEL":
                EmailService(
                    to_emails=[instructeur.email],
                    email_template_id=EmailTemplateID.I_MENSUEL,
                ).send_transactional_email(
                    email_data={
                        "firstname": instructeur.first_name,
                        "lastname": instructeur.last_name,
                        "conventions_instruction": [
                            {"nom": str(c), "uuid": str(c.uuid)}
                            for c in Convention.objects.filter(
                                statut="2. Instruction requise",
                                programme__administration__in=User.objects.filter(
                                    username=instructeur.username
                                ).values("roles__administration"),
                            )
                        ],
                        "conventions_asigner": [
                            {"nom": str(c), "uuid": str(c.uuid)}
                            for c in Convention.objects.filter(
                                statut="4. A signer",
                                conventionhistories__user=instructeur,
                            )
                        ],
                    }
                )
                nb_sent_emails["instructeur"] += 1
            elif instructeur.preferences_email == "TOUS":
                EmailService(
                    to_emails=[instructeur.email],
                    email_template_id=EmailTemplateID.I_MENSUEL,
                ).send_transactional_email(
                    email_data={
                        "firstname": instructeur.first_name,
                        "lastname": instructeur.last_name,
                        "conventions_instruction": [
                            {
                                "nom": str(c),
                                "uuid": str(c.uuid),
                                "url": settings.APPLICATION_DOMAIN_URL
                                + reverse("conventions:recapitulatif", args=[c.uuid]),
                            }
                            for c in Convention.objects.filter(
                                statut="2. Instruction requise",
                                programme__administration__in=User.objects.filter(
                                    username=instructeur.username
                                ).values("roles__administration"),
                            )
                        ],
                        "conventions_asigner": [
                            {
                                "nom": str(c),
                                "uuid": str(c.uuid),
                                "url": settings.APPLICATION_DOMAIN_URL
                                + reverse("conventions:recapitulatif", args=[c.uuid]),
                            }
                            for c in Convention.objects.filter(
                                statut="4. A signer",
                                programme__administration__in=User.objects.filter(
                                    username=instructeur.username
                                ).values("roles__administration"),
                            )
                        ],
                    }
                )
                nb_sent_emails["instructeur"] += 1

        # liste des bailleurs concernés par le mail
        # ceux qui ont coché la case "tous"
        bailleurs_tous_mails = Q(
            roles__typologie="BAILLEUR",
            preferences_email="TOUS",
            roles__bailleur__programme__conventions__statut__in=[
                "1. Projet",
                "3. Corrections requises",
            ],
        )
        # "partiel" : on importe ceux qui ont créé au moins un projet de convention en cours
        bailleurs_partiel_projet = Q(
            roles__typologie="BAILLEUR",
            preferences_email="PARTIEL",
            convention__statut="1. Projet",
        )
        # "partiel" : on importe ceux qui ont validé au moins une convention en statut de correction
        bailleurs_partiel_corrections = Q(
            roles__typologie="BAILLEUR",
            preferences_email="PARTIEL",
            valide_par__convention__statut="3. Corrections requises",
        )

        for bailleur in (
            User.objects.filter(cerbere_login__isnull=True)
            .filter(
                bailleurs_tous_mails
                | bailleurs_partiel_projet
                | bailleurs_partiel_corrections
            )
            .distinct()
        ):

            if bailleur.preferences_email == "PARTIEL":
                # on importe toutes les conventions en projet créées par le bailleur
                # conventions en corrections créées par le bailleur ou soumise par lui

                EmailService(
                    to_emails=[bailleur.email],
                    email_template_id=EmailTemplateID.B_MENSUEL,
                ).send_transactional_email(
                    email_data={
                        "firstname": bailleur.first_name,
                        "lastname": bailleur.last_name,
                        "conventions_projet": [
                            {
                                "nom": str(c),
                                "uuid": str(c.uuid),
                                "url": settings.APPLICATION_DOMAIN_URL
                                + reverse("conventions:recapitulatif", args=[c.uuid]),
                            }
                            for c in Convention.objects.filter(
                                statut="1. Projet",
                                cree_par=bailleur,
                            )
                        ],
                        "conventions_correction": [
                            {
                                "nom": str(c),
                                "uuid": str(c.uuid),
                                "url": settings.APPLICATION_DOMAIN_URL
                                + reverse("conventions:recapitulatif", args=[c.uuid]),
                            }
                            for c in Convention.objects.filter(
                                Q(statut="3. Corrections requises", cree_par=bailleur)
                                | Q(
                                    statut="3. Corrections requises",
                                    conventionhistories__user=bailleur,
                                )
                            )
                        ],
                    }
                )
                nb_sent_emails["bailleur"] += 1
            elif bailleur.preferences_email == "TOUS":
                EmailService(
                    to_emails=[bailleur.email],
                    email_template_id=EmailTemplateID.B_MENSUEL,
                ).send_transactional_email(
                    email_data={
                        "firstname": bailleur.first_name,
                        "lastname": bailleur.last_name,
                        "conventions_projet": [
                            {
                                "nom": str(c),
                                "uuid": str(c.uuid),
                                "url": settings.APPLICATION_DOMAIN_URL
                                + reverse("conventions:recapitulatif", args=[c.uuid]),
                            }
                            for c in Convention.objects.filter(
                                statut="1. Projet",
                                programme__bailleur__in=User.objects.filter(
                                    username=bailleur.username
                                ).values("roles__bailleur"),
                            )
                        ],
                        "conventions_correction": [
                            {
                                "nom": str(c),
                                "uuid": str(c.uuid),
                                "url": settings.APPLICATION_DOMAIN_URL
                                + reverse("conventions:recapitulatif", args=[c.uuid]),
                            }
                            for c in Convention.objects.filter(
                                statut="3. Corrections requises",
                                programme__bailleur__in=User.objects.filter(
                                    username=bailleur.username
                                ).values("roles__bailleur"),
                            )
                        ],
                    }
                )
                nb_sent_emails["bailleur"] += 1

        return nb_sent_emails
