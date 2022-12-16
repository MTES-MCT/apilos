from conventions.forms import ConventionFoyerAttributionForm
from conventions.services import utils
from conventions.services.services_conventions import ConventionService


class ConventionFoyerAttributionService(ConventionService):
    form: ConventionFoyerAttributionForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def _get_attribution_type(self):
        return self.convention.attribution_type

    def get(self):
        self.form = ConventionFoyerAttributionForm(
            initial={
                "uuid": self.convention.uuid,
                "attribution_type": self._get_attribution_type(),
                "attribution_agees_autonomie": self.convention.attribution_agees_autonomie,
                "attribution_agees_ephad": self.convention.attribution_agees_ephad,
                "attribution_agees_desorientees": self.convention.attribution_agees_desorientees,
                "attribution_agees_petite_unite": self.convention.attribution_agees_petite_unite,
                "attribution_agees_autre": self.convention.attribution_agees_autre,
                "attribution_agees_autre_detail": self.convention.attribution_agees_autre_detail,
                "attribution_handicapes_foyer": self.convention.attribution_handicapes_foyer,
                "attribution_handicapes_foyer_de_vie": (
                    self.convention.attribution_handicapes_foyer_de_vie
                ),
                "attribution_handicapes_foyer_medicalise": (
                    self.convention.attribution_handicapes_foyer_medicalise
                ),
                "attribution_handicapes_autre": self.convention.attribution_handicapes_autre,
                "attribution_handicapes_autre_detail": (
                    self.convention.attribution_handicapes_autre_detail
                ),
                "attribution_inclusif_conditions_specifiques": (
                    self.convention.attribution_inclusif_conditions_specifiques
                ),
                "attribution_inclusif_conditions_admission": (
                    self.convention.attribution_inclusif_conditions_admission
                ),
                "attribution_inclusif_modalites_attribution": (
                    self.convention.attribution_inclusif_modalites_attribution
                ),
                "attribution_inclusif_partenariats": (
                    self.convention.attribution_inclusif_partenariats
                ),
                "attribution_inclusif_activites": self.convention.attribution_inclusif_activites,
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
        self.form = ConventionFoyerAttributionForm(self.request.POST)
        if self.form.is_valid():
            self._save_convention_attribution()
            self.return_status = utils.ReturnStatus.SUCCESS

    def _save_convention_attribution(self):
        if self.form.cleaned_data["attribution_type"] == "agees":
            for field in [
                "attribution_agees_autonomie",
                "attribution_agees_ephad",
                "attribution_agees_desorientees",
                "attribution_agees_petite_unite",
                "attribution_agees_autre",
                "attribution_agees_autre_detail",
            ]:
                _set_from_form_or_object(field, self.form, self.convention)

            self.convention.attribution_handicapes_foyer = False
            self.convention.attribution_handicapes_foyer_de_vie = False
            self.convention.attribution_handicapes_foyer_medicalise = False
            self.convention.attribution_handicapes_autre = False
            self.convention.attribution_handicapes_autre_detail = ""

            self.convention.attribution_inclusif_conditions_specifiques = ""
            self.convention.attribution_inclusif_conditions_admission = ""
            self.convention.attribution_inclusif_modalites_attribution = ""
            self.convention.attribution_inclusif_partenariats = ""
            self.convention.attribution_inclusif_activites = ""

        if self.form.cleaned_data["attribution_type"] == "handicapees":
            self.convention.attribution_agees_autonomie = False
            self.convention.attribution_agees_ephad = False
            self.convention.attribution_agees_desorientees = False
            self.convention.attribution_agees_petite_unite = False
            self.convention.attribution_agees_autre = False
            self.convention.attribution_agees_autre_detail = ""

            for field in [
                "attribution_handicapes_foyer",
                "attribution_handicapes_foyer_de_vie",
                "attribution_handicapes_foyer_medicalise",
                "attribution_handicapes_autre",
                "attribution_handicapes_autre_detail",
            ]:
                _set_from_form_or_object(field, self.form, self.convention)

            self.convention.attribution_inclusif_conditions_specifiques = ""
            self.convention.attribution_inclusif_conditions_admission = ""
            self.convention.attribution_inclusif_modalites_attribution = ""
            self.convention.attribution_inclusif_partenariats = ""
            self.convention.attribution_inclusif_activites = ""

        if self.form.cleaned_data["attribution_type"] == "inclusif":
            self.convention.attribution_agees_autonomie = False
            self.convention.attribution_agees_ephad = False
            self.convention.attribution_agees_desorientees = False
            self.convention.attribution_agees_petite_unite = False
            self.convention.attribution_agees_autre = False
            self.convention.attribution_agees_autre_detail = ""

            self.convention.attribution_handicapes_foyer = False
            self.convention.attribution_handicapes_foyer_de_vie = False
            self.convention.attribution_handicapes_foyer_medicalise = False
            self.convention.attribution_handicapes_autre = False
            self.convention.attribution_handicapes_autre_detail = ""

            for field in [
                "attribution_inclusif_conditions_specifiques",
                "attribution_inclusif_conditions_admission",
                "attribution_inclusif_modalites_attribution",
                "attribution_inclusif_partenariats",
                "attribution_inclusif_activites",
            ]:
                _set_from_form_or_object(field, self.form, self.convention)

        for field in [
            "attribution_reservation_prefectoral",
            "attribution_modalites_reservations",
            "attribution_modalites_choix_personnes",
            "attribution_prestations_integrees",
            "attribution_prestations_facultatives",
        ]:
            _set_from_form_or_object(field, self.form, self.convention)

        self.convention.save()


def _set_from_form_or_object(field, form, obj):
    setattr(
        obj,
        field,
        form.cleaned_data[field]
        if form.cleaned_data[field] is not None
        else getattr(obj, field),
    )
