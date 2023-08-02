from abc import ABC
from typing import List
from django.forms import Form
from django.http.request import HttpRequest

from conventions.forms import UploadForm
from conventions.forms.convention_date_signature import ConventionDateForm
from conventions.forms.resiliation import ConventionResiliationForm
from conventions.models import Convention, ConventionStatut
from conventions.services import utils
from conventions.services.file import ConventionFileService
from conventions.services.search import AvenantListSearchService


class ConventionService(ABC):
    convention: Convention
    request: HttpRequest
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    import_warnings: None | List = None
    redirect_recap: bool = False
    editable_after_upload: bool = False
    form: Form = None
    formset = None
    upform = None

    def __init__(
        self,
        convention: Convention,
        request: HttpRequest,
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
        "upform": upform,
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
    paginated_avenants = avenant_search_service.paginate()
    total_avenants = convention.avenants.all().count()

    return {
        "success": result_status,
        "upform": upform,
        "convention": convention,
        "avenants": paginated_avenants.get_page(request.GET.get("page", 1)),
        "total_avenants": total_avenants,
        "resiliation_form": resiliation_form,
        "updatedate_form": updatedate_form,
        "form_posted": form_posted,
    }
