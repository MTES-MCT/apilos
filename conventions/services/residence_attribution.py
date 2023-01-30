from conventions.forms import ConventionResidenceAttributionForm
from conventions.services import utils
from conventions.services.conventions import ConventionService


class ConventionResidenceAttributionService(ConventionService):
    form: ConventionResidenceAttributionForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def get(self):
        self.form = ConventionResidenceAttributionForm(
            initial={
                "uuid": self.convention.uuid,
                "attribution_reservation_prefectoral": (
                    self.convention.attribution_reservation_prefectoral
                ),
                "attribution_modalites_reservations": (
                    self.convention.attribution_modalites_reservations
                ),
                "attribution_modalites_choix_personnes": (
                    self.convention.attribution_modalites_choix_personnes
                ),
                "attribution_prestations_integrees": (
                    self.convention.attribution_prestations_integrees
                ),
                "attribution_prestations_facultatives": (
                    self.convention.attribution_prestations_facultatives
                ),
            }
        )

    def save(self):
        self.form = ConventionResidenceAttributionForm(self.request.POST)
        if self.form.is_valid():
            self._save_convention_attribution()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_convention_attribution(self):
        for field in [
            "attribution_reservation_prefectoral",
            "attribution_modalites_reservations",
            "attribution_modalites_choix_personnes",
            "attribution_prestations_integrees",
            "attribution_prestations_facultatives",
        ]:
            utils.set_from_form_or_object(field, self.form, self.convention)
        self.convention.save()
