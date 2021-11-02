from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings

from programmes.models import (
    TypeHabitat,
    TypeOperation,
    TypologieLogement,
    TypologieAnnexe,
    TypologieStationnement,
    FinancementEDD,
)
from conventions.services import services, utils, instruction_services
from conventions.models import Preteur

NB_STEPS = 11


# @permission_required("convention.view_convention")
def index(request):
    conventions = services.conventions_index(request, {})
    return render(
        request,
        "conventions/index.html",
        {"conventions": conventions, "filter": request.user.convention_filter()},
    )


@permission_required("convention.add_convention")
def select_programme_create(request):
    # STEP 1
    result = services.select_programme_create(request)
    if result["success"] == utils.ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:bailleur", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/selection.html",
        {
            **result,
            "nb_steps": NB_STEPS,
            "convention_form_step": 1,
            "financements": FinancementEDD,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
def select_programme_update(request, convention_uuid):
    # STEP 1
    result = services.select_programme_update(request, convention_uuid)
    if result["success"] == utils.ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:bailleur", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/selection.html",
        {
            **result,
            "nb_steps": NB_STEPS,
            "convention_form_step": 1,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
def bailleur(request, convention_uuid):
    # STEP 2
    result = services.bailleur_update(request, convention_uuid)
    if result["success"] == utils.ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:programme", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/bailleur.html",
        {
            **result,
            "nb_steps": NB_STEPS,
            "convention_form_step": 2,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
def programme(request, convention_uuid):
    # STEP 3
    result = services.programme_update(request, convention_uuid)
    if result["success"] == utils.ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:cadastre", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/programme.html",
        {
            **result,
            "nb_steps": NB_STEPS,
            "convention_form_step": 3,
            "types_habitat": TypeHabitat,
            "types_operation": TypeOperation,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
def cadastre(request, convention_uuid):
    # STEP 4
    result = services.programme_cadastral_update(request, convention_uuid)
    if result["success"] == utils.ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:edd", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/cadastre.html",
        {
            **result,
            "typologies": TypologieLogement,
            "nb_steps": NB_STEPS,
            "convention_form_step": 4,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
def edd(request, convention_uuid):
    # STEP 5
    result = services.programme_edd_update(request, convention_uuid)
    if result["success"] == utils.ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:prets", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/edd.html",
        {
            **result,
            "financements": FinancementEDD,
            "typologies": TypologieLogement,
            "nb_steps": NB_STEPS,
            "convention_form_step": 5,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
def prets(request, convention_uuid):
    result = services.convention_financement(request, convention_uuid)
    if result["success"] == utils.ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:logements", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/prets.html",
        {
            **result,
            "nb_steps": NB_STEPS,
            "convention_form_step": 6,
            "preteurs": Preteur,
            "years": range(2021, 2121),
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
def logements(request, convention_uuid):
    result = services.logements_update(request, convention_uuid)
    if result["success"] == utils.ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:annexes", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/logements.html",
        {
            **result,
            "nb_steps": NB_STEPS,
            "convention_form_step": 7,
            "typologies": TypologieLogement,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
def annexes(request, convention_uuid):
    result = services.annexes_update(request, convention_uuid)
    if result["success"] == utils.ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:stationnements", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/annexes.html",
        {
            **result,
            "nb_steps": NB_STEPS,
            "convention_form_step": 8,
            "typologies": TypologieAnnexe,
            "logement_typologies": TypologieLogement,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
def stationnements(request, convention_uuid):
    result = services.stationnements_update(request, convention_uuid)
    if result["success"] == utils.ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:comments", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/stationnements.html",
        {
            **result,
            "nb_steps": NB_STEPS,
            "convention_form_step": 9,
            "typologies": TypologieStationnement,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
def comments(request, convention_uuid):
    result = services.convention_comments(request, convention_uuid)
    if result["success"] == utils.ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:recapitulatif", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/comments.html",
        {
            **result,
            "nb_steps": NB_STEPS,
            "convention_form_step": 10,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention", raise_exception=True)
def recapitulatif(request, convention_uuid):
    # Step 11/11
    result = instruction_services.convention_summary(request, convention_uuid)
    return render(
        request,
        "conventions/recapitulatif.html",
        {
            **result,
            "nb_steps": NB_STEPS,
            "convention_form_step": 11,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
def save_convention(request, convention_uuid):
    result = instruction_services.convention_save(request, convention_uuid)
    if result["success"] == utils.ReturnStatus.SUCCESS:
        return render(
            request,
            "conventions/submitted.html",
            result,
        )
    if result["success"] == utils.ReturnStatus.WARNING:
        return render(
            request,
            "conventions/saved.html",
            result,
        )
    return HttpResponseRedirect(
        reverse("conventions:recapitulatif", args=[result["convention"].uuid])
    )


# Handle in service.py
# @permission_required("convention.change_convention")
def validate_convention(request, convention_uuid):
    result = instruction_services.convention_validate(request, convention_uuid)
    return HttpResponseRedirect(
        reverse("conventions:recapitulatif", args=[result["convention"].uuid])
    )


# Handle in service.py
# @permission_required("convention.change_convention")
def generate_convention(request, convention_uuid):
    data, file_name = instruction_services.generate_convention(convention_uuid)

    response = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingm",
    )
    response["Content-Disposition"] = f"attachment; filename={file_name}.docx"
    return response


#   return send_file(file_stream, as_attachment=True, attachment_filename='report_'+user_id+'.docx')


def load_xlsx_model(request, file_type):
    filepath = f"{settings.BASE_DIR}/static/files/{file_type}.xlsx"

    with open(filepath, "rb") as excel:
        data = excel.read()

    response = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f"attachment; filename={file_type}.xlsx"
    return response
