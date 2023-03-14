from abc import ABC
from typing import List

from dataclasses import dataclass

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import (
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from conventions.models import Convention

from conventions.permissions import has_campaign_permission
from conventions.services.conventions import (
    ConventionService,
)
from conventions.services.utils import (
    base_convention_response_error,
    editable_convention,
    ReturnStatus,
)


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
    label="EDD",
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

avenant_commentaires_step = ConventionFormStep(
    pathname="conventions:avenant_commentaires",
    label="Commentaires",
    classname="AvenantCommentsView",
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
    steps: List[ConventionFormStep]
    convention: Convention
    total_step_number: int
    current_step_number: int
    current_step: ConventionFormStep
    next_step: ConventionFormStep
    previous_step: ConventionFormStep | None = None

    last_step_path: ConventionFormStep = ConventionFormStep(
        pathname="conventions:recapitulatif", label="Récapitulatif", classname=None
    )

    def __init__(self, *, convention, active_classname=None) -> None:
        # pylint: disable=R0912
        self.convention = convention
        if convention.is_avenant():
            if active_classname is None:
                if (
                    convention.programme.is_foyer()
                    or convention.programme.is_residence()
                ):
                    self.steps = [
                        avenant_bailleur_step,
                        avenant_financement_step,
                        avenant_foyer_residence_logements_step,
                        avenant_collectif_step,
                        avenant_commentaires_step,
                    ]
                else:
                    self.steps = [
                        avenant_bailleur_step,
                        avenant_financement_step,
                        avenant_logements_step,
                        avenant_annexes_step,
                        avenant_commentaires_step,
                    ]
            else:
                if active_classname == "AvenantBailleurView":
                    self.steps = [avenant_bailleur_step]
                if active_classname in [
                    "AvenantLogementsView",
                    "AvenantAnnexesView",
                ]:
                    self.steps = [avenant_logements_step, avenant_annexes_step]
                if active_classname in [
                    "AvenantFoyerResidenceLogementsView",
                    "AvenantCollectifView",
                ]:
                    self.steps = [
                        avenant_foyer_residence_logements_step,
                        avenant_collectif_step,
                    ]
                if active_classname == "AvenantFinancementView":
                    self.steps = [avenant_financement_step]
                if active_classname == "AvenantCommentsView":
                    self.steps = [avenant_commentaires_step]
        elif convention.programme.is_foyer():
            self.steps = foyer_steps
        elif convention.programme.is_residence():
            self.steps = residence_steps
        else:
            self.steps = hlm_sem_type_steps

        self.total_step_number = len(self.steps)

        if active_classname is not None:
            step_index = [
                i
                for i, elem in enumerate(self.steps)
                if elem.classname == active_classname
            ][0]
            self.current_step_number = step_index + 1
            self.current_step = self.steps[step_index]
            self.next_step = (
                self.steps[step_index + 1]
                if self.current_step_number < self.total_step_number
                else self.last_step_path
            )
            if step_index > 0:
                self.previous_step = self.steps[step_index - 1]

    def get_form_step(self):
        form_step = {
            "steps": self.steps,
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


class ConventionView(ABC, LoginRequiredMixin, View):
    convention: Convention
    steps: ConventionFormSteps
    target_template: str
    service_class: ConventionService

    def _get_convention(self, convention_uuid):
        return Convention.objects.get(uuid=convention_uuid)

    @property
    def next_path_redirect(self):
        return self.steps.next_path_redirect()

    def current_path_redirect(self):
        return self.steps.current_step_path()

    # pylint: disable=W0221
    def setup(self, request, convention_uuid, *args, **kwargs):
        self.convention = self._get_convention(convention_uuid)
        self.steps = ConventionFormSteps(
            convention=self.convention, active_classname=self.__class__.__name__
        )
        return super().setup(request, convention_uuid, *args, **kwargs)

    # pylint: disable=W0613
    @has_campaign_permission("convention.view_convention")
    def get(self, request, convention_uuid):
        service = self.service_class(convention=self.convention, request=request)
        service.get()
        return render(
            request,
            self.target_template,
            {
                **base_convention_response_error(request, service.convention),
                **({"form": service.form} if service.form else {}),
                **({"upform": service.upform} if service.upform else {}),
                **({"formset": service.formset} if service.formset else {}),
                "form_step": self.steps.get_form_step(),
                "editable_after_upload": (
                    editable_convention(request, self.convention)
                    or service.editable_after_upload
                ),
            },
        )

    # pylint: disable=W0613
    @has_campaign_permission("convention.change_convention")
    def post(self, request, convention_uuid):
        service = self.service_class(convention=self.convention, request=request)
        service.save()
        if service.return_status == ReturnStatus.SUCCESS:
            if service.redirect_recap:
                return HttpResponseRedirect(
                    reverse("conventions:recapitulatif", args=[self.convention.uuid])
                )
            return HttpResponseRedirect(
                reverse(self.next_path_redirect, args=[self.convention.uuid])
            )
        if service.return_status == ReturnStatus.REFRESH:
            return HttpResponseRedirect(
                reverse(self.current_path_redirect, args=[self.convention.uuid])
            )
        return render(
            request,
            self.target_template,
            {
                **base_convention_response_error(request, service.convention),
                **({"form": service.form} if service.form else {}),
                **({"upform": service.upform} if service.upform else {}),
                **({"formset": service.formset} if service.formset else {}),
                "form_step": self.steps.get_form_step(),
                **(
                    {"import_warnings": service.import_warnings}
                    if service.import_warnings
                    else {}
                ),
                "editable_after_upload": editable_convention(request, self.convention)
                or service.editable_after_upload,
            },
        )
