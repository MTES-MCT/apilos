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
from .models import Preteur
from . import services
from .services import ReturnStatus

NB_STEPS = 11

@permission_required("convention.view_convention")
def index(request):
    conventions = services.conventions_index(request, {})
    return render(
        request,
        "conventions/index.html",
        {"conventions": conventions, "filter": request.user.convention_filter()},
    )


@permission_required("convention.change_convention")
def select_programme_create(request):
    # STEP 1
    result = services.select_programme_create(request)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:bailleur", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/selection.html",
        {"form": result["form"], "programmes": result["programmes"]},
    )


@permission_required("convention.change_convention")
def select_programme_update(request, convention_uuid):
    # STEP 1
    result = services.select_programme_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:bailleur", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/selection.html",
        {
            "form": result["form"],
            "convention_uuid": result["convention_uuid"],
            "programmes": result["programmes"],
            "nb_steps": NB_STEPS,
            "convention_form_step": 1,
        },
    )


@permission_required("convention.change_convention")
def bailleur(request, convention_uuid):
    # STEP 2
    result = services.bailleur_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:programme", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/bailleur.html",
        {
            "form": result["form"],
            "convention": result["convention"],
            "nb_steps": NB_STEPS,
            "convention_form_step": 2,
        },
    )


@permission_required("convention.change_convention")
def programme(request, convention_uuid):
    # STEP 3
    result = services.programme_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:cadastre", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/programme.html",
        {
            "form": result["form"],
            "convention": result["convention"],
            "nb_steps": NB_STEPS,
            "convention_form_step": 3,
            "types_habitat": TypeHabitat,
            "types_operation": TypeOperation,
        },
    )


@permission_required("convention.change_convention")
def cadastre(request, convention_uuid):
    # STEP 4
    result = services.programme_cadastral_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:edd", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/cadastre.html",
        {
            "upform": result["upform"],
            "form": result["form"],
            "formset": result["formset"],
            "convention": result["convention"],
            "typologies": TypologieLogement,
            "nb_steps": NB_STEPS,
            "convention_form_step": 4,
            "import_warnings": result["import_warnings"],
        },
    )


@permission_required("convention.change_convention")
def edd(request, convention_uuid):
    # STEP 5
    result = services.programme_edd_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:prets", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/edd.html",
        {
            "upform": result["upform"],
            "form": result["form"],
            "formset": result["formset"],
            "convention": result["convention"],
            "financements": FinancementEDD,
            "typologies": TypologieLogement,
            "nb_steps": NB_STEPS,
            "convention_form_step": 5,
            "import_warnings": result["import_warnings"],
        },
    )


@permission_required("convention.change_convention")
def prets(request, convention_uuid):
    result = services.convention_financement(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:logements", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/prets.html",
        {
            "upform": result["upform"],
            "form": result["form"],
            "formset": result["formset"],
            "convention": result["convention"],
            "nb_steps": NB_STEPS,
            "convention_form_step": 6,
            "preteurs": Preteur,
            "import_warnings": result["import_warnings"],
        },
    )


@permission_required("convention.change_convention")
def logements(request, convention_uuid):
    result = services.logements_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:annexes", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/logements.html",
        {
            "upform": result["upform"],
            "formset": result["formset"],
            "convention": result["convention"],
            "nb_steps": NB_STEPS,
            "convention_form_step": 7,
            "typologies": TypologieLogement,
            "import_warnings": result["import_warnings"],
        },
    )


@permission_required("convention.change_convention")
def annexes(request, convention_uuid):
    result = services.annexes_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:stationnements", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/annexes.html",
        {
            "upform": result["upform"],
            "formset": result["formset"],
            "convention": result["convention"],
            "nb_steps": NB_STEPS,
            "convention_form_step": 8,
            "typologies": TypologieAnnexe,
            "logement_typologies": TypologieLogement,
            "import_warnings": result["import_warnings"],
        },
    )

@permission_required("convention.change_convention")
def stationnements(request, convention_uuid):
    result = services.stationnements_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:comments", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/stationnements.html",
        {
            "upform": result["upform"],
            "formset": result["formset"],
            "convention": result["convention"],
            "nb_steps": NB_STEPS,
            "convention_form_step": 9,
            "typologies": TypologieStationnement,
            "import_warnings": result["import_warnings"],
        },
    )


@permission_required("convention.change_convention")
def comments(request, convention_uuid):
    result = services.convention_comments(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:recapitulatif", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/comments.html",
        {
            "form": result["form"],
            "convention": result["convention"],
            "nb_steps": NB_STEPS,
            "convention_form_step": 10,
        },
    )

@permission_required("convention.change_convention")
def generate_convention(request, convention_uuid):
    data, file_name = services.generate_convention(convention_uuid)

    response = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingm",
    )
    response["Content-Disposition"] = f"attachment; filename={file_name}.docx"
    return response


@permission_required("convention.change_convention")
def recapitulatif(request, convention_uuid):
    #Step 11/11
    result = services.convention_summary(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return render(
            request,
            "conventions/submitted.html",
            {
                "convention": result["convention"],
            },
        )
    if result["success"] == ReturnStatus.WARNING:
        return render(
            request,
            "conventions/saved.html",
            {
                "convention": result["convention"],
            },
        )
    return render(
        request,
        "conventions/recapitulatif.html",
        {
            "convention": result["convention"],
            "bailleur": result["bailleur"],
            "programme": result["programme"],
            "logement_edds": result["logement_edds"],
            "reference_cadastrales": result["reference_cadastrales"],
            "lot": result["lot"],
            "logements": result["logements"],
            "annexes": result["annexes"],
            "stationnements": result["stationnements"],
            "nb_steps": NB_STEPS,
            "convention_form_step": 11,
        },
    )


#   return send_file(file_stream, as_attachment=True, attachment_filename='report_'+user_id+'.docx')

def load_xlsx_model(request, convention_uuid, file_type):
    filepath = f'{settings.BASE_DIR}/static/files/{file_type}.xlsx'
    print(f'load_xlsx_model {file_type}.xlsx for convention_uuid {convention_uuid}')

    with open(filepath, "rb") as excel:
        data = excel.read()

    response = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f"attachment; filename={file_type}.xlsx"
    return response
