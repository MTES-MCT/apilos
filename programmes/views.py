from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from siap.siap_client.client import SIAPClient
from siap.siap_client.utils import get_or_create_conventions


@login_required
def operation_conventions(request, numero_operation):

    # Décorator ?
    if not request.user.is_cerbere_user():
        raise PermissionError("this function is available only for CERBERE user")

    client = SIAPClient.get_instance()
    operation = client.get_operation(
        user_login=request.user.cerbere_login,
        habilitation_id=request.session["habilitation_id"],
        operation_identifier=numero_operation,
    )
    (programme, lots, conventions) = get_or_create_conventions(operation)

    return render(
        request,
        "operations/conventions.html",
        {
            "numero_operation": numero_operation,
            "programme": programme,
            "lots": lots,
            "conventions": conventions,
        },
    )
