from abc import ABC, abstractmethod

from django.forms import Form

from conventions.forms import UploadForm
from conventions.forms.convention_form_dates import (
    ConventionDatePublicationForm,
    ConventionDateResiliationForm,
    ConventionDateSignatureForm,
)
from conventions.forms.convention_form_resiliation import ConventionResiliationForm
from conventions.models import Convention, ConventionStatut
from conventions.services import utils
from conventions.services.search import AvenantListSearchService
from core.request import AuthenticatedHttpRequest


class ConventionService(ABC):
    convention: Convention
    request: AuthenticatedHttpRequest
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    import_warnings: None | list = None
    redirect_recap: bool = False
    editable_after_upload: bool = False
    form: Form | None = None
    formset = None
    formset_list: list | None = []
    formset_sans_loyer = None
    formset_corrigee = None
    formset_corrigee_sans_loyer = None
    formset_convention_mixte = None
    upform: Form | None = None
    extra_forms: dict[str, Form | None] | None = None

    def __init__(
        self,
        convention: Convention,
        request: AuthenticatedHttpRequest,
    ):
        self.convention = convention
        self.request = request

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def save(self):
        pass


def convention_post_action(request, convention_uuid):
    convention = Convention.objects.get(uuid=convention_uuid)
    result_status = None
    form_posted = None
    if request.method == "POST":
        resiliation_form = ConventionResiliationForm(request.POST)
        signature_date_form = ConventionDateSignatureForm(request.POST)
        resiliation_date_form = ConventionDateResiliationForm(request.POST)
        publication_spf_date_form = ConventionDatePublicationForm(request.POST)
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
            if signature_date_form.is_valid():
                convention.televersement_convention_signee_le = (
                    signature_date_form.cleaned_data[
                        "televersement_convention_signee_le"
                    ]
                )
                convention.save()
                result_status = utils.ReturnStatus.SUCCESS
                form_posted = "date_signature"
            elif resiliation_date_form.is_valid():
                convention.date_resiliation = resiliation_date_form.cleaned_data[
                    "date_resiliation"
                ]
                convention.save()
                result_status = utils.ReturnStatus.SUCCESS
                form_posted = "date_resiliation"
            elif publication_spf_date_form.is_valid():
                convention.date_publication_spf = (
                    publication_spf_date_form.cleaned_data["date_publication_spf"]
                )
                convention.save()
                result_status = utils.ReturnStatus.SUCCESS
                form_posted = "publication_spf_date"

    else:
        resiliation_form = ConventionResiliationForm()
        signature_date_form = ConventionDateSignatureForm()
        resiliation_date_form = ConventionDateResiliationForm

    upform = UploadForm()
    avenant_search_service = AvenantListSearchService(
        convention, order_by="televersement_convention_signee_le"
    )
    total_avenants = convention.avenants.without_denonciation_and_resiliation().count()
    denonciation = convention.avenants.filter(avenant_types__nom__in=["denonciation"])
    resiliation = convention.avenants.filter(avenant_types__nom__in=["resiliation"])

    return {
        "success": result_status,
        "upform": upform,  # Obsolète: cette approche sera dépréciée dans le futur, au profit de extra_forms.
        "extra_forms": {
            "upform": upform,
        },
        "convention": convention,
        "avenants": avenant_search_service.paginate().get_page(
            request.GET.get("page", 1)
        ),
        "total_avenants": total_avenants,
        "denonciation": denonciation,
        "resiliation": resiliation,
        "resiliation_form": resiliation_form,
        "signature_date_form": signature_date_form,
        "resiliation_date_form": resiliation_date_form,
        "form_posted": form_posted,
        "publication_spf_date_form": ConventionDatePublicationForm(
            initial={
                "date_publication_spf": (
                    convention.date_publication_spf.strftime("%Y-%m-%d")
                    if convention.date_publication_spf
                    else ""
                ),
            }
        ),
    }
