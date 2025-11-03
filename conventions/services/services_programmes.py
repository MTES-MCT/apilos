from django.http import HttpRequest

from conventions.forms import ProgrammeForm, ProgrammeMinimalForm
from conventions.models import Convention
from conventions.services import utils
from conventions.services.conventions import ConventionService
from programmes.models import Lot, Programme


class ConventionProgrammeService(ConventionService):
    convention: Convention
    request: HttpRequest
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    form: ProgrammeForm
    redirect_recap: bool = False

    def get(self):
        programme = self.convention.programme
        self.form = ProgrammeForm(
            initial={
                "uuid": programme.uuid,
                "nom": programme.nom,
                "adresse": self.convention.adresse or programme.adresse,
                "code_postal": programme.code_postal,
                "ville": programme.ville,
                "type_habitat": self.convention.lots.first().type_habitat,
                "type_operation": programme.type_operation,
                "anru": programme.anru,
                "anah": programme.anah,
                "autres_locaux_hors_convention": programme.autres_locaux_hors_convention,
                "nb_locaux_commerciaux": programme.nb_locaux_commerciaux,
                "nb_bureaux": programme.nb_bureaux,
            }
        )

    def get_avenant(self):
        programme = self.convention.programme
        self.form = ProgrammeMinimalForm(
            initial={
                "uuid": programme.uuid,
                "nom": programme.nom,
                "adresse": programme.adresse,
            }
        )

    def save(self):
        self.redirect_recap = bool(self.request.POST.get("redirect_to_recap", False))
        self._programme_atomic_update()

    def _programme_atomic_update(self):
        self.form = ProgrammeForm(
            {
                "uuid": self.convention.programme.uuid,
                "type_habitat": self.request.POST.get(
                    "type_habitat",
                    self.convention.lots.first().type_habitat,
                ),
                **utils.build_partial_form(
                    self.request,
                    self.convention.programme,
                    [
                        "nom",
                        "adresse",
                        "code_postal",
                        "ville",
                        "type_operation",
                        "anru",
                        "anah",
                        "autres_locaux_hors_convention",
                        "nb_locaux_commerciaux",
                        "nb_bureaux",
                    ],
                ),
            }
        )
        if self.form.is_valid():
            _save_convention_adresse(self.convention, self.form)
            _save_programme_and_lot(
                self.convention.programme, self.convention.lots.all(), self.form
            )
            self.return_status = utils.ReturnStatus.SUCCESS


def _save_programme_and_lot(programme: Programme, lots: list[Lot], form: ProgrammeForm):
    programme.nom = form.cleaned_data["nom"]
    programme.code_postal = form.cleaned_data["code_postal"]
    programme.ville = form.cleaned_data["ville"]
    if form.cleaned_data["type_operation"]:
        programme.type_operation = form.cleaned_data["type_operation"]
    programme.anru = form.cleaned_data["anru"]
    programme.anah = form.cleaned_data["anah"]
    programme.autres_locaux_hors_convention = form.cleaned_data[
        "autres_locaux_hors_convention"
    ]
    programme.nb_locaux_commerciaux = form.cleaned_data["nb_locaux_commerciaux"]
    programme.nb_bureaux = form.cleaned_data["nb_bureaux"]
    programme.save()

    # Set the same type_habitat for all lots (case convention mixte)
    for lot in lots:
        lot.type_habitat = form.cleaned_data["type_habitat"]
        lot.save()


def _save_convention_adresse(convention: Convention, form: ProgrammeForm):
    convention.adresse = form.cleaned_data["adresse"]
    convention.save()
