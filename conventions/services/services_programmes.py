from django.http import HttpRequest

from conventions.services.conventions import ConventionService
from conventions.models import Convention
from conventions.services import utils
from conventions.forms import ProgrammeForm, ProgrammeMinimalForm


class ConventionProgrammeService(ConventionService):
    convention: Convention
    request: HttpRequest
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR
    form: ProgrammeForm
    redirect_recap: bool = False

    def get(self):
        programme = self.convention.programme
        lot = self.convention.lot
        self.form = ProgrammeForm(
            initial={
                "uuid": programme.uuid,
                "nom": programme.nom,
                "adresse": programme.adresse,
                "code_postal": programme.code_postal,
                "ville": programme.ville,
                "type_habitat": lot.type_habitat,
                "type_operation": programme.type_operation,
                "anru": programme.anru,
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
                    "type_habitat", self.convention.lot.type_habitat
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
                        "autres_locaux_hors_convention",
                        "nb_locaux_commerciaux",
                        "nb_bureaux",
                    ],
                ),
            }
        )
        if self.form.is_valid():
            _save_programme_and_lot(
                self.convention.programme, self.convention.lot, self.form
            )
            self.return_status = utils.ReturnStatus.SUCCESS


def _save_programme_and_lot(programme, lot, form):
    programme.nom = form.cleaned_data["nom"]
    programme.adresse = form.cleaned_data["adresse"]
    programme.code_postal = form.cleaned_data["code_postal"]
    programme.ville = form.cleaned_data["ville"]
    if form.cleaned_data["type_operation"]:
        programme.type_operation = form.cleaned_data["type_operation"]
    programme.anru = form.cleaned_data["anru"]
    programme.autres_locaux_hors_convention = form.cleaned_data[
        "autres_locaux_hors_convention"
    ]
    programme.nb_locaux_commerciaux = form.cleaned_data["nb_locaux_commerciaux"]
    programme.nb_bureaux = form.cleaned_data["nb_bureaux"]
    programme.save()
    lot.type_habitat = form.cleaned_data["type_habitat"]
    lot.save()
