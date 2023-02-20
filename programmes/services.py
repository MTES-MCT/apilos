import functools
from datetime import date

from programmes.models import IndiceEvolutionLoyer, NatureLogement
from siap.siap_client.client import SIAPClient
from siap.siap_client.utils import get_or_create_conventions


def get_or_create_conventions_from_operation_number(request, numero_operation):
    client = SIAPClient.get_instance()
    operation = client.get_operation(
        user_login=request.user.cerbere_login,
        habilitation_id=request.session["habilitation_id"],
        operation_identifier=numero_operation,
    )
    return get_or_create_conventions(operation, request.user)


class LoyerRedevanceUpdateComputer:
    @staticmethod
    def compute_loyer_update(
        montant_initial: float,
        nature_logement: str,
        date_initiale: date,
        date_actualisation: date | None = date.today(),
    ) -> float:
        if nature_logement not in NatureLogement.values:
            raise Exception(f"Nature de logement invalide {nature_logement}")

        coefficients = list(
            IndiceEvolutionLoyer.objects.filter(
                nature_logement=nature_logement,
                annee__gt=date_initiale.year,
                annee__lt=date_actualisation.year,
            )
            .order_by("annee")
            .values_list("differentiel", flat=True)
        )

        return functools.reduce(
            lambda loyer, differentiel: loyer * ((100.0 + differentiel) / 100.0),
            coefficients,
            montant_initial,
        )
