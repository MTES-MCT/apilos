from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings

from conventions.models import Financement

from programmes.models import (
    TypeHabitat,
    TypeOperation,
    TypologieLogement,
    TypologieAnnexe,
    TypologieStationnement
)
from .models import Convention, Preteur
from . import services
from .services import ReturnStatus

NB_STEPS = 10

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
    result = services.select_programme_create(request)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:step2", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/step1.html",
        {"form": result["form"], "programmes": result["programmes"]},
    )


@permission_required("convention.change_convention")
def select_programme_update(request, convention_uuid):
    result = services.select_programme_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:step2", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/step1.html",
        {
            "form": result["form"],
            "convention_uuid": result["convention_uuid"],
            "programmes": result["programmes"],
            "nb_steps": NB_STEPS,
        },
    )


@permission_required("convention.change_convention")
def step2(request, convention_uuid):
    result = services.bailleur_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:step3", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/step2.html",
        {
            "form": result["form"],
            "convention": result["convention"],
            "nb_steps": NB_STEPS,
        },
    )


@permission_required("convention.change_convention")
def step3(request, convention_uuid):
    result = services.programme_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:step4", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/step3.html",
        {
            "form": result["form"],
            "convention": result["convention"],
            "nb_steps": NB_STEPS,
            "types_habitat": TypeHabitat,
            "types_operation": TypeOperation,
        },
    )


@permission_required("convention.change_convention")
def step4(request, convention_uuid):
    result = services.programme_cadastral_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:step5", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/step4.html",
        {
            "upform": result["upform"],
            "form": result["form"],
            "formset": result["formset"],
            "convention": result["convention"],
            "financements": Financement,
            "typologies": TypologieLogement,
            "nb_steps": NB_STEPS,
            "import_warnings": result["import_warnings"],
        },
    )


@permission_required("convention.change_convention")
def step5(request, convention_uuid):
    result = services.convention_financement(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:step6", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/step5.html",
        {
            "upform": result["upform"],
            "form": result["form"],
            "formset": result["formset"],
            "convention": result["convention"],
            "nb_steps": NB_STEPS,
            "preteurs": Preteur,
            "import_warnings": result["import_warnings"],
        },
    )


@permission_required("convention.change_convention")
def step6(request, convention_uuid):
    result = services.logements_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:step7", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/step6.html",
        {
            "upform": result["upform"],
            "formset": result["formset"],
            "convention": result["convention"],
            "nb_steps": NB_STEPS,
            "typologies": TypologieLogement,
            "import_warnings": result["import_warnings"],
        },
    )


@permission_required("convention.change_convention")
def step7(request, convention_uuid):
    result = services.annexes_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:step8", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/step7.html",
        {
            "upform": result["upform"],
            "formset": result["formset"],
            "convention": result["convention"],
            "nb_steps": NB_STEPS,
            "typologies": TypologieAnnexe,
            "logement_typologies": TypologieLogement,
            "import_warnings": result["import_warnings"],
        },
    )

@permission_required("convention.change_convention")
def step8(request, convention_uuid):
    result = services.stationnements_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:step9", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/step8.html",
        {
            "upform": result["upform"],
            "formset": result["formset"],
            "convention": result["convention"],
            "nb_steps": NB_STEPS,
            "typologies": TypologieStationnement,
            "import_warnings": result["import_warnings"],
        },
    )


@permission_required("convention.change_convention")
def step9(request, convention_uuid):
    result = services.convention_comments(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:step10", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/step9.html",
        {
            "form": result["form"],
            "convention": result["convention"],
            "nb_steps": NB_STEPS,
        },
    )



@permission_required("convention.change_convention")
def step10(request, convention_uuid):

    if request.method == "POST":
        if request.POST.get("GenerateConvention", False):
            convention = (
                Convention.objects
                    .prefetch_related("bailleur")
                    .prefetch_related("programme")
                    .prefetch_related("lot")
                    .prefetch_related("lot__typestationnement_set")
                    .prefetch_related("lot__logement_set")
                    .get(uuid=convention_uuid)
            )
            filepath = f'{settings.BASE_DIR}/documents/HLM-jinja.docx'
            print(f'load HLM docx for convention_uuid {convention_uuid}')

            with open(filepath, "rb") as docx:
                data = docx.read()

            response = HttpResponse(
                data,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingm",
            )
            response["Content-Disposition"] = f"attachment; filename={convention}.docx"
            return response


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
        "conventions/step10.html",
        {
            "convention": result["convention"],
            "bailleur": result["bailleur"],
            "programme": result["programme"],
            "lot": result["lot"],
            "logements": result["logements"],
            "annexes": result["annexes"],
            "stationnements": result["stationnements"],
            "nb_steps": NB_STEPS,
        },
    )


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
