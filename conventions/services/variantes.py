from conventions.forms import ConventionFoyerVariantesForm
from conventions.services import utils
from conventions.services.services_conventions import ConventionService


class ConventionFoyerVariantesService(ConventionService):
    form: ConventionFoyerVariantesForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def get(self):
        self.form = ConventionFoyerVariantesForm(
            initial={
                "uuid": self.convention.uuid,
                "foyer_variante_1": self.convention.foyer_variante_1,
                "foyer_variante_2": self.convention.foyer_variante_2,
                "foyer_variante_2_travaux": self.convention.foyer_variante_2_travaux,
                "foyer_variante_3": self.convention.foyer_variante_3,
            }
        )

    def save(self):
        self.form = ConventionFoyerVariantesForm(self.request.POST)
        if self.form.is_valid():
            self._save_convention_foyer_variantes()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_convention_foyer_variantes(self):
        for field in [
            "foyer_variante_1",
            "foyer_variante_2",
            "foyer_variante_3",
        ]:
            utils.set_from_form_or_object(field, self.form, self.convention)
        if self.form.cleaned_data["foyer_variante_2"]:
            utils.set_from_form_or_object(
                "foyer_variante_2_travaux", self.form, self.convention
            )
        else:
            self.convention.foyer_variante_2_travaux = ""

        self.convention.save()
