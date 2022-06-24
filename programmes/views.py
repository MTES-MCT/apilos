from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.siap_client.client import SIAPClient


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

    return render(
        request,
        "operations/conventions.html",
        {"numero_operation": numero_operation, "operation": operation},
    )
