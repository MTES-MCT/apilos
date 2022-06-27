from zipfile import ZipFile

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings

from programmes.models import FinancementEDD
from conventions.services import services
from conventions.services.utils import ReturnStatus

NB_STEPS = 12


# @permission_required("convention.view_convention")
@login_required
def index(request):
    result = services.conventions_index(request)
    return render(
        request,
        "conventions/index.html",
        {**result},
    )


@login_required
@permission_required("convention.add_convention")
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
        {
            **result,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
@login_required
def bailleur(request, convention_uuid):
    # STEP 2
    result = services.bailleur_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:programme", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/bailleur.html",
        {
            **result,
            "convention_form_step": 1,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
@login_required
def programme(request, convention_uuid):
    # STEP 3
    result = services.programme_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:cadastre", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/programme.html",
        {
            **result,
            "convention_form_step": 2,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
@login_required
def cadastre(request, convention_uuid):
    # STEP 4
    result = services.programme_cadastral_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:edd", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/cadastre.html",
        {
            **result,
            "convention_form_step": 3,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
@login_required
def edd(request, convention_uuid):
    # STEP 5
    result = services.programme_edd_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:financement", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/edd.html",
        {
            **result,
            "convention_form_step": 4,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
@login_required
def financement(request, convention_uuid):
    result = services.convention_financement(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:logements", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/financement.html",
        {
            **result,
            "convention_form_step": 5,
            "years": range(2021, 2121),
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
@login_required
def logements(request, convention_uuid):
    result = services.logements_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:annexes", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/logements.html",
        {
            **result,
            "convention_form_step": 6,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
@login_required
def annexes(request, convention_uuid):
    result = services.annexes_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:stationnements", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/annexes.html",
        {
            **result,
            "convention_form_step": 7,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
@login_required
def stationnements(request, convention_uuid):
    result = services.stationnements_update(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:comments", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/stationnements.html",
        {
            **result,
            "convention_form_step": 8,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
@login_required
def comments(request, convention_uuid):
    result = services.convention_comments(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        if result.get("redirect", False) == "recapitulatif":
            return HttpResponseRedirect(
                reverse("conventions:recapitulatif", args=[result["convention"].uuid])
            )
        return HttpResponseRedirect(
            reverse("conventions:recapitulatif", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/comments.html",
        {
            **result,
            "convention_form_step": 9,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention", raise_exception=True)
@login_required
def recapitulatif(request, convention_uuid):
    # Step 11/11
    result = services.convention_summary(request, convention_uuid)
    return render(
        request,
        "conventions/recapitulatif.html",
        {
            **result,
            "convention_form_step": 10,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
@login_required
def save_convention(request, convention_uuid):
    result = services.convention_submit(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return render(
            request,
            "conventions/submitted.html",
            result,
        )
    if result["success"] == ReturnStatus.WARNING:
        return render(
            request,
            "conventions/saved.html",
            result,
        )
    return HttpResponseRedirect(
        reverse("conventions:recapitulatif", args=[result["convention"].uuid])
    )


@login_required
def delete_convention(request, convention_uuid):
    services.convention_delete(request, convention_uuid)
    return HttpResponseRedirect(reverse("conventions:index"))


# Handle in service.py
# @permission_required("convention.change_convention")
@login_required
def feedback_convention(request, convention_uuid):
    result = services.convention_feedback(request, convention_uuid)
    return HttpResponseRedirect(
        reverse("conventions:recapitulatif", args=[result["convention"].uuid])
    )


# Handle in service.py
# @permission_required("convention.change_convention")
@login_required
def validate_convention(request, convention_uuid):
    result = services.convention_validate(request, convention_uuid)
    if result["success"] == ReturnStatus.SUCCESS:
        return HttpResponseRedirect(
            reverse("conventions:recapitulatif", args=[result["convention"].uuid])
        )
    return render(
        request,
        "conventions/recapitulatif.html",
        {
            **result,
            "convention_form_step": 10,
        },
    )


# Handle in service.py
# @permission_required("convention.change_convention")
@login_required
def generate_convention(request, convention_uuid):
    data, file_name = services.generate_convention(request, convention_uuid)

    response = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingm",
    )
    response["Content-Disposition"] = f"attachment; filename={file_name}.docx"
    return response


@login_required
def load_xlsx_model(request, file_type):
    if file_type not in [
        "annexes",
        "cadastre",
        "financement",
        "logements_edd",
        "logements",
        "stationnements",
        "all",
    ]:
        raise PermissionDenied

    if file_type == "all":
        filepath = f"{settings.BASE_DIR}/static/files/tous_les_templates_xlsx.zip"
        with ZipFile(filepath, "w") as zipObj:
            # Add multiple files to the zip
            for each_file in [
                "annexes",
                "cadastre",
                "financement",
                "logements_edd",
                "logements",
                "stationnements",
            ]:
                zipObj.write(
                    f"{settings.BASE_DIR}/static/files/{each_file}.xlsx",
                    arcname=f"{each_file}.xlsx",
                )
            zipObj.close()
        with open(filepath, "rb") as zip_file:
            # close the Zip File
            response = HttpResponse(zip_file, content_type="application/force-download")
            zip_file.close()
        response[
            "Content-Disposition"
        ] = 'attachment; filename="tous_les_templates_xlsx.zip"'
        return response

    filepath = f"{settings.BASE_DIR}/static/files/{file_type}.xlsx"

    with open(filepath, "rb") as excel:
        data = excel.read()

    response = HttpResponse(
        data,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f"attachment; filename={file_type}.xlsx"
    return response


@login_required
def display_operation(request, programme_uuid, programme_financement):
    result = services.display_operation(request, programme_uuid, programme_financement)
    if result["success"] == ReturnStatus.SUCCESS and result["convention"]:
        return HttpResponseRedirect(
            reverse("conventions:recapitulatif", args=[result["convention"].uuid])
        )
    if result["success"] == ReturnStatus.WARNING:
        return render(
            request,
            "conventions/selection.html",
            {
                **result,
                "financements": FinancementEDD,
                "redirect_action": "/conventions/selection",
            },
        )
    return PermissionDenied


# @permission_required("convention.change_convention", raise_exception=True)
@login_required
def preview(request, convention_uuid):
    # Step 11/12
    result = services.convention_preview(convention_uuid)
    filepath = f"{settings.BASE_DIR}"
    return render(
        request,
        "conventions/preview.html",
        {
            **result,
            "filepath": filepath,
            "convention_form_step": 11,
        },
    )


# @permission_required("convention.change_convention", raise_exception=True)
@login_required
def sent(request, convention_uuid):
    # Step 12/12
    result = services.convention_sent(request, convention_uuid)
    return render(
        request,
        "conventions/sent.html",
        {
            **result,
            "convention_form_step": 12,
        },
    )
