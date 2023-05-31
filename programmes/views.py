from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from conventions.services.search import ProgrammeConventionSearchService
from programmes.services import get_or_create_conventions_from_operation_number


@login_required
def operation_conventions(request, numero_operation):
    # Décorator ?
    if not request.user.is_cerbere_user():
        raise PermissionError("this function is available only for CERBERE user")

    (programme, _, _) = get_or_create_conventions_from_operation_number(
        request, numero_operation
    )

    service = ProgrammeConventionSearchService(programme)

    return render(
        request,
        "operations/conventions.html",
        {
            "numero_operation": numero_operation,
            "programme": programme,
            "conventions": service.get_results(),
        },
    )
