from django.contrib.auth.models import Group
from django.db.models import Q

from bailleurs.models import Bailleur
from conventions.models import Convention
from core.services import EmailService, EmailTemplateID
from users.models import User, Role
from users.type_models import TypeRole


class UserService:
    @classmethod
    def create_user_bailleur(
        cls,
        first_name: str,
        last_name: str,
        email: str,
        bailleur: Bailleur,
        username: str,
        login_url: str,
    ) -> User:

        user_bailleur = User.objects.create_user(
            username, email, first_name=first_name, last_name=last_name
        )
        group_bailleur = Group.objects.get(
            name="bailleur",
        )
        Role.objects.create(
            typologie=TypeRole.BAILLEUR,
            bailleur=bailleur,
            user=user_bailleur,
            group=group_bailleur,
        )

        password = User.objects.make_random_password()
        user_bailleur.set_password(password)
        user_bailleur.save()

        EmailService(
            to_emails=[user_bailleur.email],
            email_template_id=EmailTemplateID.B_WELCOME,
        ).send_transactional_email(
            email_data={
                "email": user_bailleur.email,
                "username": user_bailleur.username,
                "firstname": user_bailleur.first_name,
                "lastname": user_bailleur.last_name,
                "password": password,
                "login_url": login_url,
            }
        )

        return user_bailleur

    @classmethod
    def extract_username_from_email(cls, email: str | None = None):
        if email is None:
            return ""

        parts = email.split("@", maxsplit=1)

        if len(parts) > 1:
            return parts[0].lower()

        return ""

    @classmethod
    def email_mensuel(cls):

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

        initial_instructeur = []
        for instructeur in User.objects.filter(
            instructeur_tous_mails
            | instructeur_partiel_instruction
            | instructeur_partiel_signature
        ).distinct():
            if instructeur.preferences_email == "PARTIEL":
                initial_instructeur.append(
                    {
                        "firstname": instructeur.first_name,
                        "lastname": instructeur.last_name,
                        "email": instructeur.email,
                        "conventions_instruction": Convention.objects.filter(
                            statut="2. Instruction requise",
                            programme__administration__in=User.objects.filter(
                                username=instructeur.username
                            ).values("roles__administration"),
                        ),
                        "conventions_asigner": Convention.objects.filter(
                            statut="4. A signer", conventionhistories__user=instructeur
                        ),
                    }
                )
            elif instructeur.preferences_email == "TOUS":
                initial_instructeur.append(
                    {
                        "firstname": instructeur.first_name,
                        "lastname": instructeur.last_name,
                        "email": instructeur.email,
                        "conventions_instruction": Convention.objects.filter(
                            statut="2. Instruction requise",
                            programme__administration__in=User.objects.filter(
                                username=instructeur.username
                            ).values("roles__administration"),
                        ),
                        "conventions_asigner": Convention.objects.filter(
                            statut="4. A signer",
                            programme__administration__in=User.objects.filter(
                                username=instructeur.username
                            ).values("roles__administration"),
                        ),
                    }
                )

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

        initial_bailleur = []
        for bailleur in User.objects.filter(
            bailleurs_tous_mails
            | bailleurs_partiel_projet
            | bailleurs_partiel_corrections
        ).distinct():

            if bailleur.preferences_email == "PARTIEL":
                # on importe toutes les conventions en projet créées par le bailleur
                # conventions en corrections créées par le bailleur ou soumise par lui
                conventions_correc_cree = Q(
                    statut="3. Corrections requises", cree_par=bailleur
                )
                conventions_correc_valid = Q(
                    statut="3. Corrections requises", conventionhistories__user=bailleur
                )
                initial_bailleur.append(
                    {
                        "firstname": bailleur.first_name,
                        "lastname": bailleur.last_name,
                        "email": bailleur.email,
                        "conventions_projet": Convention.objects.filter(
                            statut="1. Projet", cree_par=bailleur
                        ),
                        "conventions_correction": Convention.objects.filter(
                            conventions_correc_cree | conventions_correc_valid
                        ),
                    }
                )
            elif bailleur.preferences_email == "TOUS":
                initial_bailleur.append(
                    {
                        "firstname": bailleur.first_name,
                        "lastname": bailleur.last_name,
                        "email": bailleur.email,
                        "conventions_projet": Convention.objects.filter(
                            statut="1. Projet",
                            programme__bailleur__in=User.objects.filter(
                                username=bailleur.username
                            ).values("roles__bailleur"),
                        ),
                        "conventions_correction": Convention.objects.filter(
                            statut="3. Corrections requises",
                            programme__bailleur__in=User.objects.filter(
                                username=bailleur.username
                            ).values("roles__bailleur"),
                        ),
                    }
                )

        return initial_instructeur, initial_bailleur
