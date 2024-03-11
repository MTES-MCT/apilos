from django.conf import settings
from django.db.models.query import QuerySet
from django.http import HttpRequest

from conventions.forms import (
    CreateConventionMinForm,
    NewConventionForm,
)
from conventions.models import Convention
from conventions.services import utils
from conventions.services.file import ConventionFileService
from conventions.templatetags.custom_filters import is_instructeur
from instructeurs.models import Administration
from programmes.models import Financement, Lot, Programme, TypeOperation


def _get_choices_from_object(object_list):
    return [(instance.uuid, str(instance)) for instance in object_list]


class ConventionSelectionService:
    request: HttpRequest
    convention: Convention
    avenant: Convention
    form: CreateConventionMinForm
    lots: QuerySet[Lot] | None = None
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    def _get_bailleur_query(self, uuid: str | None = None):
        queryset = self.request.user.bailleurs(full_scope=True)
        if uuid:
            return queryset.all()

        return queryset[0 : settings.APILOS_MAX_DROPDOWN_COUNT]

    def _get_administration_choices(self):
        return _get_choices_from_object(
            self.request.user.administrations()
            if is_instructeur(self.request)
            else Administration.objects.all().order_by("nom")
        )

    def get_create_convention(self):
        self.form = NewConventionForm(
            administrations=self._get_administration_choices(),
            bailleur_query=self._get_bailleur_query(),
        )

    def post_create_convention(self):
        bailleur_uuid = self.request.POST.get("bailleur")
        self.form = NewConventionForm(
            self.request.POST,
            self.request.FILES,
            administrations=self._get_administration_choices(),
            bailleur_query=self._get_bailleur_query(uuid=bailleur_uuid),
        )
        if self.form.is_valid():
            bailleur = self.form.cleaned_data["bailleur"]
            administration = Administration.objects.get(
                uuid=self.form.cleaned_data["administration"]
            )
            programme = Programme.objects.create(
                nom=self.form.cleaned_data["nom"],
                code_postal=self.form.cleaned_data["code_postal"],
                ville=self.form.cleaned_data["ville"],
                bailleur=bailleur,
                administration=administration,
                nature_logement=self.form.cleaned_data["nature_logement"],
                type_operation=(
                    TypeOperation.SANSTRAVAUX
                    if self.form.cleaned_data["financement"]
                    == Financement.SANS_FINANCEMENT
                    else TypeOperation.NEUF
                ),
                numero_galion=self.form.cleaned_data["numero_galion"],
                # default ANRU when it is SIAP version
                anru=bool(settings.CERBERE_AUTH),
            )
            programme.save()
            lot = Lot.objects.create(
                nb_logements=self.form.cleaned_data["nb_logements"],
                financement=self.form.cleaned_data["financement"],
                type_habitat=self.form.cleaned_data["type_habitat"],
                programme=programme,
            )
            lot.save()
            self.convention = Convention.objects.create(
                lot=lot,
                programme_id=lot.programme_id,
                financement=lot.financement,
                cree_par=self.request.user,
            )
            self.convention.save()
            file = self.request.FILES.get("nom_fichier_signe", False)
            if file:
                ConventionFileService.upload_convention_file(self.convention, file)
            self.return_status = utils.ReturnStatus.SUCCESS
