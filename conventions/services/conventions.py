from abc import ABC
from typing import Any, List

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.db.models.functions import Substr
from django.forms import Form
from django.http.request import HttpRequest

from bailleurs.models import Bailleur
from conventions.forms import UploadForm
from conventions.forms.convention_date_signature import ConventionDateForm
from conventions.forms.resiliation import ConventionResiliationForm
from conventions.models import Convention, ConventionStatut
from conventions.services import utils
from conventions.services.file import ConventionFileService
from conventions.services.search import AvenantListSearchService
from instructeurs.models import Administration
from users.models import User


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


class ConventionListService:
    # pylint: disable=R0902,R0913
    search_input: str
    order_by: str
    page: str
    statut_filter: str | None
    financement_filter: str | None
    departement_input: str | None
    ville: str | None
    anru: bool
    my_convention_list: Any  # list[Convention]
    paginated_conventions: Any  # list[Convention]
    total_conventions: int
    user: User
    bailleur: Bailleur | None
    administration: Administration | None

    def __init__(
        self,
        my_convention_list: Any,
        search_input: str = "",
        statut_filter: str | None = None,
        financement_filter: str | None = None,
        departement_input: str | None = None,
        ville: str | None = None,
        anru: bool = False,
        active: bool | None = None,
        order_by: str = "",
        page: str = 1,
        user: User | None = None,
        bailleur: Bailleur | None = None,
        administration: Administration | None = None,
    ):
        self.search_input = search_input
        try:
            self.statut = ConventionStatut[statut_filter]
        except KeyError:
            self.statut = None
        self.financement_filter = financement_filter
        self.departement_input = departement_input
        self.ville = ville
        self.anru = anru
        self.active = active
        self.order_by = order_by
        self.page = page
        self.user = user
        self.bailleur = bailleur
        self.administration = administration
        self.my_convention_list = my_convention_list

    # pylint: disable=R0912
    def paginate(self) -> None:
        total_user = self.my_convention_list.count()
        if self.search_input:
            my_filter = Q(programme__nom__icontains=self.search_input) | Q(
                programme__code_postal__icontains=self.search_input
            )
            if self.active:
                my_filter = my_filter | Q(
                    programme__numero_galion__icontains=self.search_input
                )
            else:
                my_filter = my_filter | Q(numero__icontains=self.search_input)

            self.my_convention_list = self.my_convention_list.filter(my_filter)

        if self.statut:
            self.my_convention_list = self.my_convention_list.filter(
                statut=self.statut.label
            )

        if self.financement_filter:
            self.my_convention_list = self.my_convention_list.filter(
                financement=self.financement_filter
            )

        if self.anru:
            self.my_convention_list = self.my_convention_list.filter(
                programme__anru=True
            )

        if self.ville:
            self.my_convention_list = self.my_convention_list.filter(
                programme__ville__icontains=self.ville
            )

        if self.departement_input:
            self.my_convention_list = self.my_convention_list.annotate(
                departement=Substr("programme__code_postal", 1, 2)
            ).filter(departement=self.departement_input)

        if self.bailleur:
            self.my_convention_list = self.my_convention_list.filter(
                lot__programme__bailleur=self.bailleur
            )

        if self.administration:
            self.my_convention_list = self.my_convention_list.filter(
                lot__programme__administration=self.administration
            )

        if self.order_by:
            self.my_convention_list = self.my_convention_list.order_by(self.order_by)

        paginator = Paginator(
            self.my_convention_list, settings.APILOS_PAGINATION_PER_PAGE
        )
        try:
            conventions = paginator.page(self.page)
        except PageNotAnInteger:
            conventions = paginator.page(1)
        except EmptyPage:
            conventions = paginator.page(paginator.num_pages)

        self.paginated_conventions = conventions
        self.total_conventions = total_user


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
    paginator = avenant_search_service.paginate()
    total_avenants = convention.avenants.all().count()

    return {
        "success": result_status,
        "upform": upform,
        "convention": convention,
        "avenants": paginator.get_page(request.GET.get("page", 1)),
        "total_avenants": total_avenants,
        "resiliation_form": resiliation_form,
        "updatedate_form": updatedate_form,
        "form_posted": form_posted,
    }
