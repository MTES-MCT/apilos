import logging
from typing import Any

from django.urls import reverse

from conventions.models.alerte_siap_log import (
    AlerteSIAPLog,
    AlerteSIAPOperation,
    AlerteSIAPStatut,
)
from conventions.models.convention import Convention
from conventions.templatetags.display_filters import (
    display_gender_terminaison,
    display_kind,
)
from siap.exceptions import SIAPException
from siap.siap_client.client import SIAPClient
from siap.siap_client.schemas import Alerte, Destinataire

logger = logging.getLogger(__name__)


ALERTE_CATEGORY_MAPPING = {
    "action": "CATEGORIE_ALERTE_ACTION",
    "information": "CATEGORIE_ALERTE_INFORMATION",
}

ALERTE_DESTINATAIRE_MO = Destinataire(role="INSTRUCTEUR", service="MO")

ALERTE_DESTINATAIRE_SG = Destinataire(role="INSTRUCTEUR", service="SG")

ALERTE_TYPE_CHANGEMENT_STATUT = "Changement de statut"

ALERTE_ETIQUETTE_CUSTOM = "CUSTOM"


class AlerteService:
    convention: Convention
    siap_credentials: dict[str, Any]

    def __init__(self, convention, siap_credentials):
        self.convention = convention
        self.siap_credentials = siap_credentials

    def _send_alerte(self, alerte: Alerte, description: str) -> bool:
        """
        Envoie une alerte SIAP et log le résultat (succès ou échec).
        Retourne True si l'alerte a été envoyée avec succès, False sinon.
        """
        payload_json = alerte.to_json()
        payload_dict = alerte.to_dict()
        user_login = self.siap_credentials.get("user_login", "")
        habilitation_id = self.siap_credentials.get("habilitation_id", "")
        logger.info(
            "[ALERTE SIAP] Envoi %s | convention=%s | destinataires=%s | "
            "etiquette=%s | user_login=%s | habilitation_id=%s",
            description,
            self.convention.uuid,
            payload_dict.get("destinataires", []),
            payload_dict.get("etiquettePersonnalisee", ""),
            user_login or "N/A",
            habilitation_id or "N/A",
        )
        try:
            SIAPClient.get_instance().create_alerte(
                payload=payload_json, **self.siap_credentials
            )
            logger.info(
                "[ALERTE SIAP] OK %s | convention=%s",
                description,
                self.convention.uuid,
            )
            AlerteSIAPLog.objects.create(
                convention=self.convention,
                operation=AlerteSIAPOperation.CREATION,
                statut=AlerteSIAPStatut.ENVOYEE,
                description=description,
                destinataires=payload_dict.get("destinataires", []),
                etiquette=payload_dict.get("etiquettePersonnalisee", ""),
                user_login=user_login,
                habilitation_id=str(habilitation_id),
                payload=payload_dict,
            )
            return True
        except SIAPException as e:
            logger.error(
                "[ALERTE SIAP] ECHEC %s | convention=%s | erreur=%s",
                description,
                self.convention.uuid,
                e,
            )
            AlerteSIAPLog.objects.create(
                convention=self.convention,
                operation=AlerteSIAPOperation.CREATION,
                statut=AlerteSIAPStatut.ECHEC,
                description=description,
                destinataires=payload_dict.get("destinataires", []),
                etiquette=payload_dict.get("etiquettePersonnalisee", ""),
                user_login=user_login,
                habilitation_id=str(habilitation_id),
                payload=payload_dict,
                erreur=str(e),
            )
            return False

    def delete_action_alertes(self):
        """
        Delete all action alertes related to the convention
        """
        client = SIAPClient.get_instance()
        logger.info(
            "[ALERTE SIAP] Suppression alertes action | convention=%s | "
            "user_login=%s | habilitation_id=%s",
            self.convention.uuid,
            self.siap_credentials.get("user_login", "N/A"),
            self.siap_credentials.get("habilitation_id", "N/A"),
        )
        alertes = client.list_convention_alertes(
            convention_id=self.convention.uuid, **self.siap_credentials
        )
        logger.info(
            "[ALERTE SIAP] %d alertes trouvées pour convention=%s",
            len(alertes),
            self.convention.uuid,
        )
        for alerte in alertes:

            if alerte["categorie"] != ALERTE_CATEGORY_MAPPING["action"]:
                continue

            try:
                client.delete_alerte(
                    user_login=self.siap_credentials["user_login"],
                    habilitation_id=self.siap_credentials["habilitation_id"],
                    alerte_id=alerte["id"],
                )
                logger.info(
                    "[ALERTE SIAP] Alerte action %s supprimée | convention=%s",
                    alerte["id"],
                    self.convention.uuid,
                )
                AlerteSIAPLog.objects.create(
                    convention=self.convention,
                    operation=AlerteSIAPOperation.SUPPRESSION,
                    statut=AlerteSIAPStatut.ENVOYEE,
                    description=f"Suppression alerte action {alerte['id']}",
                    user_login=self.siap_credentials.get("user_login", ""),
                    habilitation_id=str(
                        self.siap_credentials.get("habilitation_id", "")
                    ),
                )
            except SIAPException as e:
                logger.warning(
                    "[ALERTE SIAP] Echec suppression alerte %s | convention=%s | erreur=%s",
                    alerte["id"],
                    self.convention.uuid,
                    e,
                )
                AlerteSIAPLog.objects.create(
                    convention=self.convention,
                    operation=AlerteSIAPOperation.SUPPRESSION,
                    statut=AlerteSIAPStatut.ECHEC,
                    description=f"Suppression alerte action {alerte['id']}",
                    user_login=self.siap_credentials.get("user_login", ""),
                    habilitation_id=str(
                        self.siap_credentials.get("habilitation_id", "")
                    ),
                    erreur=str(e),
                )

    def create_alertes_instruction(self):
        redirect_url = reverse("conventions:recapitulatif", args=[self.convention.uuid])

        # Send an information notice to bailleurs
        alerte = Alerte.from_convention(
            convention=self.convention,
            categorie_information=ALERTE_CATEGORY_MAPPING["information"],
            destinataires=[
                ALERTE_DESTINATAIRE_MO,
            ],
            etiquette=ALERTE_ETIQUETTE_CUSTOM,
            etiquette_personnalisee=f"{display_kind(self.convention).capitalize()} en instruction",
            type_alerte=ALERTE_TYPE_CHANGEMENT_STATUT,
            url_direction=redirect_url,
        )
        self._send_alerte(alerte, "instruction -> information MO")

        # Send an action notice to instructeurs
        alerte = Alerte.from_convention(
            convention=self.convention,
            categorie_information=ALERTE_CATEGORY_MAPPING["action"],
            destinataires=[
                ALERTE_DESTINATAIRE_SG,
            ],
            etiquette=ALERTE_ETIQUETTE_CUSTOM,
            etiquette_personnalisee=f"{display_kind(self.convention).capitalize()} à instruire",
            type_alerte=ALERTE_TYPE_CHANGEMENT_STATUT,
            url_direction=redirect_url,
        )
        self._send_alerte(alerte, "instruction -> action SG")

    def create_alertes_correction(self, from_instructeur: bool):
        redirect_url = reverse("conventions:recapitulatif", args=[self.convention.uuid])
        if from_instructeur:
            destinataires_information = [ALERTE_DESTINATAIRE_SG]
            etiquette_personnalisee_information = (
                f"{display_kind(self.convention).capitalize()} en correction"
            )
            destinataires_action = [ALERTE_DESTINATAIRE_MO]
            etiquette_personnalisee_action = (
                f"{display_kind(self.convention).capitalize()} à corriger"
            )

        else:
            destinataires_information = [ALERTE_DESTINATAIRE_MO]
            etiquette_personnalisee_information = (
                f"{display_kind(self.convention).capitalize()} en instruction"
            )
            destinataires_action = [ALERTE_DESTINATAIRE_SG]
            etiquette_personnalisee_action = (
                f"{display_kind(self.convention).capitalize()} à instruire à nouveau"
            )

        # Send information notice
        alerte = Alerte.from_convention(
            convention=self.convention,
            categorie_information=ALERTE_CATEGORY_MAPPING["information"],
            destinataires=destinataires_information,
            etiquette=ALERTE_ETIQUETTE_CUSTOM,
            etiquette_personnalisee=etiquette_personnalisee_information,
            type_alerte=ALERTE_TYPE_CHANGEMENT_STATUT,
            url_direction=redirect_url,
        )
        self._send_alerte(
            alerte, f"correction -> information {'SG' if from_instructeur else 'MO'}"
        )

        # Send action notice
        alerte = Alerte.from_convention(
            convention=self.convention,
            categorie_information=ALERTE_CATEGORY_MAPPING["action"],
            destinataires=destinataires_action,
            etiquette=ALERTE_ETIQUETTE_CUSTOM,
            etiquette_personnalisee=etiquette_personnalisee_action,
            type_alerte=ALERTE_TYPE_CHANGEMENT_STATUT,
            url_direction=redirect_url,
        )
        self._send_alerte(
            alerte, f"correction -> action {'MO' if from_instructeur else 'SG'}"
        )

    def create_alertes_valide(self):
        redirect_url = reverse("conventions:preview", args=[self.convention.uuid])

        # Information notice to bailleurs
        alerte = Alerte.from_convention(
            convention=self.convention,
            categorie_information=ALERTE_CATEGORY_MAPPING["action"],
            destinataires=[ALERTE_DESTINATAIRE_MO],
            etiquette=ALERTE_ETIQUETTE_CUSTOM,
            etiquette_personnalisee=(
                f"{display_kind(self.convention).capitalize()} "
                f"validé{display_gender_terminaison(self.convention)} à signer"
            ),
            type_alerte=ALERTE_TYPE_CHANGEMENT_STATUT,
            url_direction=redirect_url,
        )
        self._send_alerte(alerte, "valide -> action MO (a signer)")

        # Action notice to instructeurs
        alerte = Alerte.from_convention(
            convention=self.convention,
            categorie_information=ALERTE_CATEGORY_MAPPING["action"],
            destinataires=[ALERTE_DESTINATAIRE_SG],
            etiquette=ALERTE_ETIQUETTE_CUSTOM,
            etiquette_personnalisee=(
                f"{display_kind(self.convention).capitalize()} "
                f"validé{display_gender_terminaison(self.convention)} à signer"
            ),
            type_alerte=ALERTE_TYPE_CHANGEMENT_STATUT,
            url_direction=redirect_url,
        )
        self._send_alerte(alerte, "valide -> action SG (a signer)")

    def create_alertes_signed(self):
        redirect_url = reverse("conventions:preview", args=[self.convention.uuid])
        alerte = Alerte.from_convention(
            convention=self.convention,
            categorie_information=ALERTE_CATEGORY_MAPPING["information"],
            destinataires=[
                ALERTE_DESTINATAIRE_MO,
                ALERTE_DESTINATAIRE_SG,
            ],
            etiquette=ALERTE_ETIQUETTE_CUSTOM,
            etiquette_personnalisee=f"{display_kind(self.convention).capitalize()} "
            f"signé{display_gender_terminaison(self.convention)}",
            type_alerte=ALERTE_TYPE_CHANGEMENT_STATUT,
            url_direction=redirect_url,
        )
        self._send_alerte(alerte, "signe -> information MO+SG")

    def create_alertes_publication_en_cours(self):
        redirect_url = reverse("conventions:recapitulatif", args=[self.convention.uuid])

        alerte = Alerte.from_convention(
            convention=self.convention,
            categorie_information=ALERTE_CATEGORY_MAPPING["information"],
            destinataires=[ALERTE_DESTINATAIRE_SG],
            etiquette=ALERTE_ETIQUETTE_CUSTOM,
            etiquette_personnalisee=(
                f"{display_kind(self.convention).capitalize()} "
                f"en cours de publication"
            ),
            type_alerte=ALERTE_TYPE_CHANGEMENT_STATUT,
            url_direction=redirect_url,
        )
        self._send_alerte(alerte, "publication en cours -> information SG")

    def create_alertes_publie(self):
        redirect_url = reverse("conventions:recapitulatif", args=[self.convention.uuid])

        alerte = Alerte.from_convention(
            convention=self.convention,
            categorie_information=ALERTE_CATEGORY_MAPPING["information"],
            destinataires=[ALERTE_DESTINATAIRE_SG],
            etiquette=ALERTE_ETIQUETTE_CUSTOM,
            etiquette_personnalisee=(
                f"{display_kind(self.convention).capitalize()} "
                f"publié{display_gender_terminaison(self.convention)}"
            ),
            type_alerte=ALERTE_TYPE_CHANGEMENT_STATUT,
            url_direction=redirect_url,
        )
        self._send_alerte(alerte, "publie -> information SG")
