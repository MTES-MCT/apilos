from dataclasses import asdict
from datetime import date
from pprint import pprint

from conventions.models import Convention, ConventionStatut
from siap.siap_client.services import create_siap_alerte
from siap.siap_client.client import SIAPClient, SIAPClientRemote
from siap.siap_client.schemas import Alerte, Destinataire

habilitation_id = "17840"
user_email = 'sylvain.delabye@beta.gouv.fr'


def call_siap_alertes():

    siap_client: SIAPClientRemote = SIAPClient.get_instance()

    print("List alertes")
    for alerte in siap_client.list_alertes(
        user_login=user_email, habilitation_id=habilitation_id
    ):
        pprint(alerte)

    convention = Convention.objects.filter(
        statut=ConventionStatut.INSTRUCTION.label,
    ).order_by("-cree_le").first()

    alerte = Alerte.from_convention(
        convention=convention,
        categorie_information="CATEGORIE_ALERTE_ACTION",
        destinataires=[
            Destinataire(role="INSTRUCTEUR", service="MO"),
        ],
        etiquette="CUSTOM",
        etiquette_personnalisee="Convention à instruire",
        type_alerte="Changement de statut",
        url_direction="/",
    )

    pprint(alerte.to_json())

    resp = create_siap_alerte(
        alerte,
        user_login=user_email,
        habilitation_id=habilitation_id,
    )

    # pprint(resp)


call_siap_alertes()