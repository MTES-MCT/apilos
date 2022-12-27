from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.db.models.query import QuerySet

from conventions.models import (
    ConventionStatut,
)

from conventions.templatetags.custom_filters import is_instructeur
from conventions.models import Convention
from conventions.services import utils
from conventions.services.file import ConventionFileService
from core.services import EmailService
from instructeurs.models import Administration
from bailleurs.models import Bailleur
from programmes.models import (
    Financement,
    Programme,
    Lot,
    TypeOperation,
)
from programmes.subforms.lot_selection import (
    ProgrammeSelectionFromDBForm,
    ProgrammeSelectionFromZeroForm,
)


def _get_choices_from_object(object_list):
    return [(instance.uuid, str(instance)) for instance in object_list]


class ConventionSelectionService:
    request: HttpRequest
    convention: Convention
    form: ProgrammeSelectionFromDBForm | ProgrammeSelectionFromZeroForm
    lots: QuerySet[Lot] | None = None
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    def _get_bailleur_choices(self):
        return _get_choices_from_object(
            Bailleur.objects.all().order_by("nom")
            if is_instructeur(self.request)
            else self.request.user.bailleurs()
        )

    def _get_administration_choices(self):
        return _get_choices_from_object(
            self.request.user.administrations()
            if is_instructeur(self.request)
            else Administration.objects.all().order_by("nom")
        )

    def get_from_zero(self):
        self.form = ProgrammeSelectionFromZeroForm(
            bailleurs=self._get_bailleur_choices(),
            administrations=self._get_administration_choices(),
        )

    def post_from_zero(self):
        self.form = ProgrammeSelectionFromZeroForm(
            self.request.POST,
            self.request.FILES,
            bailleurs=self._get_bailleur_choices(),
            administrations=self._get_administration_choices(),
        )
        if self.form.is_valid():
            bailleur = Bailleur.objects.get(uuid=self.form.cleaned_data["bailleur"])
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
                statut=(
                    ConventionStatut.SIGNEE
                    if self.form.cleaned_data["statut"]
                    else ConventionStatut.PROJET
                ),
                numero=(
                    self.form.cleaned_data["numero"]
                    if self.form.cleaned_data["numero"]
                    else ""
                ),
            )
            _send_email_staff(self.request, self.convention)
            self.convention.save()
            file = self.request.FILES.get("nom_fichier_signe", False)
            if file:
                ConventionFileService.upload_convention_file(self.convention, file)
            self.return_status = utils.ReturnStatus.SUCCESS

    def get_from_db(self):
        self.lots = (
            self.request.user.lots()
            .prefetch_related("programme")
            .prefetch_related("conventions")
            .order_by(
                "programme__ville", "programme__nom", "nb_logements", "financement"
            )
            .filter(programme__parent_id__isnull=True)
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
            .filter(programme__parent_id__isnull=True)
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


def _send_email_staff(request, convention):
    # envoi d'un mail au staff APiLos lors de la création from scratch
    convention_url = request.build_absolute_uri(
        reverse("conventions:recapitulatif", args=[convention.uuid])
    )
    text_content = render_to_string(
        "emails/alert_create_convention.txt",
        {
            "convention_url": convention_url,
            "convention": convention,
            "programme": convention.programme,
            "user": request.user,
        },
    )
    html_content = render_to_string(
        "emails/alert_create_convention.html",
        {
            "convention_url": convention_url,
            "convention": convention,
            "programme": convention.programme,
            "user": request.user,
        },
    )

    subject = f"[{settings.ENVIRONMENT.upper()}] "
    subject += f"Nouvelle convention créée de zéro ({convention})"
    EmailService(
        subject=subject,
        text_content=text_content,
        html_content=html_content,
    ).send_to_devs()
