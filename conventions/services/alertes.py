import logging
import re
from typing import Any

from django.urls import reverse

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

    def _is_ddt(self):
        return bool(re.match(r"^DD\d+$", self.convention.programme.administration.code))

    def delete_action_alertes(self):
        """
        Delete all action alertes related to the convention
        """
        client = SIAPClient.get_instance()
        alertes = client.list_convention_alertes(
            convention_id=self.convention.uuid, **self.siap_credentials
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
            except SIAPException as e:
                logger.warning(e)

    def create_alertes_instruction(self):
        if self._is_ddt():
            return
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

        SIAPClient.get_instance().create_alerte(
            payload=alerte.to_json(), **self.siap_credentials
        )

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

        SIAPClient.get_instance().create_alerte(
            payload=alerte.to_json(), **self.siap_credentials
        )

    def create_alertes_correction(self, from_instructeur: bool):
        if self._is_ddt():
            return
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
        SIAPClient.get_instance().create_alerte(
            payload=alerte.to_json(),
            **self.siap_credentials,
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
        SIAPClient.get_instance().create_alerte(
            payload=alerte.to_json(), **self.siap_credentials
        )

    def create_alertes_valide(self):
        if self._is_ddt():
            return
        redirect_url = reverse("conventions:preview", args=[self.convention.uuid])

        # Information notice to bailleurs
        alerte = Alerte.from_convention(
            convention=self.convention,
            # Pas sûr on a mis information / action sur le doc
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
        SIAPClient.get_instance().create_alerte(
            payload=alerte.to_json(),
            **self.siap_credentials,
        )

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
        SIAPClient.get_instance().create_alerte(
            payload=alerte.to_json(),
            **self.siap_credentials,
        )

    def create_alertes_signed(self):
        if self._is_ddt():
            return
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

        SIAPClient.get_instance().create_alerte(
            payload=alerte.to_json(), **self.siap_credentials
        )
