from abc import ABC
from dataclasses import dataclass
from typing import Any

from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View

from conventions.models import Convention
from conventions.permissions import currentrole_campaign_permission_required
from conventions.services.conventions import ConventionService
from conventions.services.utils import (
    ReturnStatus,
    base_convention_response_error,
    editable_convention,
)
from core.views import SetupLoginRequiredMixin


@dataclass
class ConventionFormStep:
    pathname: str
    label: str
    classname: str | None


bailleur_step = ConventionFormStep(
    pathname="conventions:bailleur",
    label="Bailleur",
    classname="ConventionBailleurView",
)

programme_step = ConventionFormStep(
    pathname="conventions:programme",
    label="Opération",
    classname="ConventionProgrammeView",
)

cadastre_step = ConventionFormStep(
    pathname="conventions:cadastre",
    label="Cadastre",
    classname="ConventionCadastreView",
)

edd_step = ConventionFormStep(
    pathname="conventions:edd",
    label="États descriptifs de division",
    classname="ConventionEDDView",
)

financement_step = ConventionFormStep(
    pathname="conventions:financement",
    label="Financement",
    classname="ConventionFinancementView",
)

logements_step = ConventionFormStep(
    pathname="conventions:logements",
    label="Logements",
    classname="ConventionLogementsView",
)

foyer_residence_logements_step = ConventionFormStep(
    pathname="conventions:foyer_residence_logements",
    label="Logements",
    classname="ConventionFoyerResidenceLogementsView",
)

annexes_step = ConventionFormStep(
    pathname="conventions:annexes",
    label="Annexes",
    classname="ConventionAnnexesView",
)

collectif_step = ConventionFormStep(
    pathname="conventions:collectif",
    label="Collectif",
    classname="ConventionCollectifView",
)

stationnements_step = ConventionFormStep(
    pathname="conventions:stationnements",
    label="Stationnements",
    classname="ConventionTypeStationnementView",
)

foyer_attribution_step = ConventionFormStep(
    pathname="conventions:foyer_attribution",
    label="Attribution",
    classname="ConventionFoyerAttributionView",
)

residence_attribution_step = ConventionFormStep(
    pathname="conventions:residence_attribution",
    label="Attribution",
    classname="ConventionResidenceAttributionView",
)

foyer_variante_step = ConventionFormStep(
    pathname="conventions:variantes",
    label="Variantes",
    classname="ConventionFoyerVariantesView",
)

commentaires_step = ConventionFormStep(
    pathname="conventions:commentaires",
    label="Commentaires",
    classname="ConventionCommentairesView",
)

avenant_bailleur_step = ConventionFormStep(
    pathname="conventions:avenant_bailleur",
    label="Bailleur",
    classname="AvenantBailleurView",
)
avenant_programme_step = ConventionFormStep(
    pathname="conventions:avenant_programme",
    label="Programme",
    classname="AvenantProgrammeView",
)

avenant_logements_step = ConventionFormStep(
    pathname="conventions:avenant_logements",
    label="Logements",
    classname="AvenantLogementsView",
)

avenant_foyer_residence_logements_step = ConventionFormStep(
    pathname="conventions:avenant_foyer_residence_logements",
    label="Logements",
    classname="AvenantFoyerResidenceLogementsView",
)

avenant_annexes_step = ConventionFormStep(
    pathname="conventions:avenant_annexes",
    label="Annexes",
    classname="AvenantAnnexesView",
)

avenant_collectif_step = ConventionFormStep(
    pathname="conventions:avenant_collectif",
    label="Collectif",
    classname="AvenantCollectifView",
)

avenant_financement_step = ConventionFormStep(
    pathname="conventions:avenant_financement",
    label="Financement",
    classname="AvenantFinancementView",
)

avenant_champ_libre_step = ConventionFormStep(
    pathname="conventions:avenant_champ_libre",
    label="Champ libre",
    classname="AvenantChampLibreView",
)

avenant_commentaires_step = ConventionFormStep(
    pathname="conventions:avenant_commentaires",
    label="Commentaires",
    classname="AvenantCommentsView",
)

avenant_denonciation_step = ConventionFormStep(
    pathname="conventions:denonciation",
    label="Dénonciation",
    classname="DenonciationView",
)

avenant_resiliation_demande_step = ConventionFormStep(
    pathname="conventions:resiliation_start",
    label="Création de la résiliation",
    classname="ResiliationView",
)

avenant_resiliation_creation_step = ConventionFormStep(
    pathname="conventions:resiliation_creation",
    label="Création de la résiliation",
    classname="ResiliationCreationView",
)

avenant_resiliation_acte_step = ConventionFormStep(
    pathname="conventions:resiliation_acte",
    label="Instruction de la résiliation",
    classname="ResiliationActeView",
)

hlm_sem_type_steps = [
    bailleur_step,
    programme_step,
    cadastre_step,
    edd_step,
    financement_step,
    logements_step,
    annexes_step,
    stationnements_step,
    commentaires_step,
]

foyer_steps = [
    bailleur_step,
    programme_step,
    cadastre_step,
    edd_step,
    financement_step,
    foyer_residence_logements_step,
    collectif_step,
    foyer_attribution_step,
    foyer_variante_step,
    commentaires_step,
]

residence_steps = [
    bailleur_step,
    programme_step,
    cadastre_step,
    edd_step,
    financement_step,
    foyer_residence_logements_step,
    collectif_step,
    residence_attribution_step,
    foyer_variante_step,
    commentaires_step,
]


class ConventionFormSteps:
    steps: list[ConventionFormStep] | None
    convention: Convention
    last_step_path: ConventionFormStep = ConventionFormStep(
        pathname="conventions:recapitulatif", label="Récapitulatif", classname=None
    )

    def __init__(
        self,
        *,
        convention,
        request,
        steps: list[ConventionFormStep] | None = None,
        active_classname=None
    ) -> None:
        self.convention = convention
        self.steps = steps

        if not self.steps:
            if convention.is_avenant():
                varying_steps = (
                    [avenant_foyer_residence_logements_step, avenant_collectif_step]
                    if convention.programme.is_foyer()
                    or convention.programme.is_residence()
                    else [
                        avenant_logements_step,
                        avenant_annexes_step,
                    ]
                )
                self.steps = [
                    avenant_bailleur_step,
                    avenant_programme_step,
                    avenant_financement_step,
                    *varying_steps,
                    avenant_champ_libre_step,
                    avenant_commentaires_step,
                ]

            elif convention.programme.is_foyer():
                self.steps = foyer_steps
            elif convention.programme.is_residence():
                self.steps = residence_steps
            else:
                self.steps = hlm_sem_type_steps

        if active_classname:
            self.step_index = [
                i
                for i, elem in enumerate(self.steps)
                if elem.classname == active_classname
            ][0]

    @property
    def total_step_number(self) -> int:
        return len(self.steps)

    @property
    def current_step_number(self) -> int:
        return self.step_index + 1

    @property
    def current_step(self) -> ConventionFormStep:
        return self.steps[self.step_index]

    @property
    def next_step(self) -> ConventionFormStep:
        if self.current_step_number < self.total_step_number:
            return self.steps[self.step_index + 1]

        return self.last_step_path

    @property
    def previous_step(self) -> ConventionFormStep | None:
        if self.step_index > 0:
            return self.steps[self.step_index - 1]

        return None

    def get_form_step(self):
        form_step = {
            "number": self.current_step_number,
            "total": self.total_step_number,
            "title": self.current_step.label,
            "next": self.next_step.label,
            "next_target": self.next_step.pathname,
        }
        if self.previous_step is not None:
            form_step.update(
                {
                    "previous": self.previous_step.label,
                    "previous_target": self.previous_step.pathname,
                }
            )
        return form_step

    def next_path_redirect(self):
        return self.next_step.pathname

    def current_step_path(self):
        return self.current_step.pathname


class BaseConventionView(SetupLoginRequiredMixin, View):
    convention: Convention

    def _get_convention(self, convention_uuid):
        return get_object_or_404(Convention, uuid=convention_uuid)

    def logged_in_setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        self.convention = self._get_convention(kwargs.get("convention_uuid"))


class ConventionView(ABC, BaseConventionView):
    steps: ConventionFormSteps
    form_steps: list[ConventionFormStep]
    target_template: str
    service_class: ConventionService
    request: HttpRequest
    service: ConventionService
    redirect_on_success: str

    @property
    def next_path_redirect(self):
        return self.steps.next_path_redirect()

    def current_path_redirect(self):
        return self.steps.current_step_path()

    def logged_in_setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        super().logged_in_setup(request, *args, **kwargs)

        form_steps = None
        try:
            form_steps = self.form_steps
        except AttributeError:
            pass

        self.steps = ConventionFormSteps(
            convention=self.convention,
            request=request,
            steps=form_steps,
            active_classname=type(self).__name__,
        )

    @currentrole_campaign_permission_required("convention.view_convention")
    def get(self, request, **kwargs):
        service = self.service_class(convention=self.convention, request=request)
        service.get()
        return render(
            request,
            self.target_template,
            {
                **base_convention_response_error(request, service.convention),
                **({"form": service.form} if service.form else {}),
                **({"extra_forms": service.extra_forms} if service.extra_forms else {}),
                **({"formset": service.formset} if service.formset else {}),
                **({"formset_sans_loyer": service.formset_sans_loyer} if service.formset_sans_loyer else {}),
                **({"formset_corrigee": service.formset_corrigee} if service.formset_corrigee else {}),
                **({"formset_corrigee_sans_loyer": service.formset_corrigee_sans_loyer} if service.formset_corrigee_sans_loyer else {}),
                # TODO: obsolète, pourra être supprimé après rédaction de tests unitaires sur extra_forms
                "upform": service.upform,
                "form_step": self.steps.get_form_step(),
                "editable_after_upload": (
                    editable_convention(request, self.convention)
                    or service.editable_after_upload
                ),
            },
        )

    def post_action(self):
        self.service.save()

    @currentrole_campaign_permission_required("convention.change_convention")
    def post(self, request, convention_uuid):
        self.request = request
        self.service = self.service_class(convention=self.convention, request=request)
        self.post_action()
        if self.service.return_status == ReturnStatus.SUCCESS:
            if self.service.redirect_recap:
                return HttpResponseRedirect(
                    reverse("conventions:recapitulatif", args=[self.convention.uuid])
                )

            try:
                return HttpResponseRedirect(reverse(self.redirect_on_success))
            except AttributeError:
                pass

            return HttpResponseRedirect(
                reverse(self.next_path_redirect, args=[self.convention.uuid])
            )

        if self.service.return_status == ReturnStatus.REFRESH:
            return HttpResponseRedirect(
                reverse(self.current_path_redirect, args=[self.convention.uuid])
            )

        return render(
            request,
            self.target_template,
            {
                **base_convention_response_error(request, self.service.convention),
                **({"form": self.service.form} if self.service.form else {}),
                **({"upform": getattr(self.service, "upform", {})}),
                **(
                    {"extra_forms": self.service.extra_forms}
                    if self.service.extra_forms
                    else {}
                ),
                **({"formset": self.service.formset} if self.service.formset else {}),
                **({"formset_sans_loyer": self.service.formset_sans_loyer} if self.service.formset_sans_loyer else {}),
                **({"formset_corrigee": self.service.formset_corrigee} if self.service.formset_corrigee else {}),
                **({"formset_corrigee_sans_loyer": self.service.formset_corrigee_sans_loyer} if self.service.formset_corrigee_sans_loyer else {}),
                "form_step": self.steps.get_form_step(),
                **(
                    {"import_warnings": self.service.import_warnings}
                    if self.service.import_warnings
                    else {}
                ),
                "editable_after_upload": editable_convention(request, self.convention)
                or self.service.editable_after_upload,
            },
        )
