from abc import ABC
from typing import List
from django.forms import Form

from conventions.forms import UploadForm
from conventions.forms.convention_date_signature import ConventionDateForm
from conventions.forms.resiliation import ConventionResiliationForm
from conventions.models import Convention, ConventionStatut
from conventions.services import utils
from conventions.services.file import ConventionFileService
from conventions.services.search import AvenantListSearchService
from core.request import AuthenticatedHttpRequest


class ConventionService(ABC):
    convention: Convention
    request: AuthenticatedHttpRequest
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    import_warnings: None | List = None
    redirect_recap: bool = False
    editable_after_upload: bool = False
    form: Form | None = None
    formset = None
    extra_forms: dict[str, Form | None] | None = None

    def __init__(
        self,
        convention: Convention,
        request: AuthenticatedHttpRequest,
    ):
        self.convention = convention
        self.request = request

    def get(self):
        pass

    def save(self):
        pass


def convention_sent(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    result_status = None
    if request.method == "POST":
        upform = UploadForm(request.POST, request.FILES)
        if upform.is_valid():
            ConventionFileService.upload_convention_file(
                convention, request.FILES["file"]
            )
            result_status = utils.ReturnStatus.SUCCESS
    else:
        upform = UploadForm()

    return {
        "success": result_status,
        "convention": convention,
        "extra_forms": {
            "upform": upform,
        },
    }


def convention_post_action(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    result_status = None
    form_posted = None
    if request.method == "POST":
        resiliation_form = ConventionResiliationForm(request.POST)
        updatedate_form = ConventionDateForm(request.POST)
        is_resiliation = request.POST.get("resiliation", False)
        if is_resiliation:
            if resiliation_form.is_valid():
                convention.statut = ConventionStatut.RESILIEE.label
                convention.date_resiliation = resiliation_form.cleaned_data[
                    "date_resiliation"
                ]
                convention.save()
                # SUCCESS
                result_status = utils.ReturnStatus.SUCCESS
                form_posted = "resiliation"
        else:
            if updatedate_form.is_valid():
                convention.televersement_convention_signee_le = (
                    updatedate_form.cleaned_data["televersement_convention_signee_le"]
                )
                convention.save()
                result_status = utils.ReturnStatus.SUCCESS
                form_posted = "date_signature"

    else:
        resiliation_form = ConventionResiliationForm()
        updatedate_form = ConventionDateForm()

    upform = UploadForm()
    avenant_search_service = AvenantListSearchService(convention, order_by_numero=True)
    total_avenants = convention.avenants.without_denonciation().count()
    denonciation = convention.avenants.filter(avenant_types__nom__in=["denonciation"])

    return {
        "success": result_status,
        "extra_forms": {
            "upform": upform,
        },
        "convention": convention,
        "avenants": avenant_search_service.paginate().get_page(
            request.GET.get("page", 1)
        ),
        "total_avenants": total_avenants,
        "denonciation": denonciation,
        "resiliation_form": resiliation_form,
        "updatedate_form": updatedate_form,
        "form_posted": form_posted,
    }
