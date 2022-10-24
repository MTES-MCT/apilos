from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from programmes.services import get_or_create_conventions_from_operation_number


@login_required
def operation_conventions(request, numero_operation):

    # Décorator ?
    if not request.user.is_cerbere_user():
        raise PermissionError("this function is available only for CERBERE user")

    (programme, lots, conventions) = get_or_create_conventions_from_operation_number(
        request, numero_operation
    )

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
