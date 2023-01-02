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


def get_or_create_avenant_on_closed_operation(request, numero_operation):
    client = SIAPClient.get_instance()
    operation = client.get_operation(
        user_login=request.user.cerbere_login,
        habilitation_id=request.session["habilitation_id"],
        operation_identifier=numero_operation,
    )
    # check if the opération in closed
    # compare operation and last convention version
    # create avenant if needed
