from conventions.forms.convention_form_administration import (
    UpdateConventionAdministrationForm,
)
from conventions.models.convention import Convention
from conventions.services import utils
from conventions.services.conventions import ConventionService
from programmes.models.models import Programme


class ConventionAdministrationService(ConventionService):
    form: UpdateConventionAdministrationForm
    return_status: utils.ReturnStatus = utils.ReturnStatus.ERROR

    def get(self):
        self.form = UpdateConventionAdministrationForm(
            initial={
                "uuid": self.convention.uuid,
            }
        )

    def save(self):
        self.request.user.check_perm("convention.change_convention", self.convention)
        self.form = UpdateConventionAdministrationForm(self.request.POST)

        if self.form.is_valid():
            if self.convention.parent:
                convention = Convention.objects.get(id=self.convention.parent.id)
            else:
                convention = self.convention

            new_administration = self.form.cleaned_data["administration"]
            avenants_to_updates = convention.avenants.all()
            conventions_to_update = [convention, *avenants_to_updates]

            Programme.objects.filter(conventions__in=conventions_to_update).update(
                administration=new_administration
            )
            self.return_status = utils.ReturnStatus.SUCCESS
