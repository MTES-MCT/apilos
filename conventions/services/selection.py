from django.http import HttpRequest
from django.db import transaction
from django.db.models.query import QuerySet
from django.db.models import Count
from django.conf import settings

from conventions.models import (
    ConventionStatut,
)

from conventions.templatetags.custom_filters import is_instructeur
from conventions.models import Convention
from conventions.services import utils
from conventions.services.file import ConventionFileService
from instructeurs.models import Administration
from programmes.models import (
    Financement,
    Programme,
    Lot,
    TypeOperation,
)
from conventions.forms import (
    ProgrammeSelectionFromDBForm,
    ProgrammeSelectionFromZeroForm,
    ConventionForAvenantForm,
    CreateConventionMinForm,
)


def _get_choices_from_object(object_list):
    return [(instance.uuid, str(instance)) for instance in object_list]


class ConventionSelectionService:
    request: HttpRequest
    convention: Convention
    avenant: Convention
    form: ProgrammeSelectionFromDBForm | CreateConventionMinForm
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

    def get_from_zero(self):
        self.form = ProgrammeSelectionFromZeroForm(
            administrations=self._get_administration_choices(),
            bailleur_query=self._get_bailleur_query(),
        )

    def get_for_avenant(self):
        self.form = ConventionForAvenantForm(
            administrations=self._get_administration_choices(),
            bailleur_query=self._get_bailleur_query(),
        )

    def post_from_zero(self):
        bailleur_uuid = self.request.POST.get("bailleur")
        self.form = ProgrammeSelectionFromZeroForm(
            self.request.POST,
            self.request.FILES,
            administrations=self._get_administration_choices(),
            bailleur_query=self._get_bailleur_query(bailleur_uuid),
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

    def post_for_avenant(self):
        bailleur_uuid = self.request.POST.get("bailleur")
        self.form = ConventionForAvenantForm(
            self.request.POST,
            self.request.FILES,
            administrations=self._get_administration_choices(),
            bailleur_query=self._get_bailleur_query(uuid=bailleur_uuid),
        )
        if self.form.is_valid():
            administration = Administration.objects.get(
                uuid=self.form.cleaned_data["administration"]
            )
            with transaction.atomic():
                programme = Programme.objects.create(
                    nom=self.form.cleaned_data["nom"],
                    code_postal=self.form.cleaned_data["code_postal"],
                    bailleur=self.form.cleaned_data["bailleur"],
                    administration=administration,
                    nature_logement=self.form.cleaned_data["nature_logement"],
                    type_operation=(
                        TypeOperation.SANSTRAVAUX
                        if self.form.cleaned_data["financement"]
                        == Financement.SANS_FINANCEMENT
                        else TypeOperation.NEUF
                    ),
                )
                programme.save()
                lot = Lot.objects.create(
                    financement=self.form.cleaned_data["financement"],
                    programme=programme,
                )
                lot.save()
                self.convention = Convention.objects.create(
                    lot=lot,
                    programme_id=lot.programme_id,
                    financement=lot.financement,
                    cree_par=self.request.user,
                    statut=(ConventionStatut.SIGNEE),
                    numero=(self.form.cleaned_data["numero"]),
                )
                self.convention.save()
                conventionfile = self.request.FILES.get("nom_fichier_signe", False)
                if conventionfile:
                    ConventionFileService.upload_convention_file(
                        self.convention, conventionfile
                    )
                self.return_status = utils.ReturnStatus.SUCCESS

                parent_convention = (
                    Convention.objects.prefetch_related("programme")
                    .prefetch_related("lot")
                    .prefetch_related("avenants")
                    .get(uuid=self.convention.uuid)
                )
                self.avenant = parent_convention.clone(
                    self.request.user, convention_origin=parent_convention
                )
                self.avenant.numero = self.form.cleaned_data["numero_avenant"]
                self.avenant.save()

    def get_from_db(self):
        self.lots = (
            self.request.user.lots()
            .select_related("programme")
            .annotate(nb_conventions=Count("conventions"))
            .order_by(
                "programme__ville", "programme__nom", "nb_logements", "financement"
            )
            .filter(programme__parent_id__isnull=True, nb_conventions=0)
        )
        self.form = ProgrammeSelectionFromDBForm(
            lots=_get_choices_from_object(self.lots),
        )

    def post_from_db(self):
        self.lots = (
            self.request.user.lots()
            .prefetch_related("programme")
            .prefetch_related("conventions")
            .order_by(
                "programme__ville", "programme__nom", "nb_logements", "financement"
            )
            .filter(programme__parent_id__isnull=True, conventions__isnull=True)
        )
        self.form = ProgrammeSelectionFromDBForm(
            self.request.POST,
            lots=_get_choices_from_object(self.lots),
        )
        if self.form.is_valid():
            lot = Lot.objects.get(uuid=self.form.cleaned_data["lot"])
            lot.programme.nature_logement = self.form.cleaned_data["nature_logement"]
            lot.programme.save()
            self.convention = Convention.objects.create(
                lot=lot,
                programme_id=lot.programme_id,
                financement=lot.financement,
                cree_par=self.request.user,
            )
            self.convention.save()
            self.return_status = utils.ReturnStatus.SUCCESS
