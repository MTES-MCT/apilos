from django import forms
from django.contrib import messages
from django.core.validators import RegexValidator
from django.shortcuts import redirect

from conventions.models.convention import Convention
from instructeurs.models import Administration
from programmes.models import Programme


class UpdateConventionAdministrationForm(forms.Form):
    administration = forms.ModelChoiceField(
        label="Administration",
        queryset=Administration.objects.all(),
        to_field_name="uuid",
        error_messages={
            "required": "Vous devez choisir une administration",
            "min_length": "min : Vous devez choisir une administration",
            "invalid_choice": "invalid : Vous devez choisir une administration",
        },
    )

    verification = forms.CharField(
        label="Vérification",
        validators=[RegexValidator("transférer")],
        required=True,
        error_messages={
            "required": "Vous devez recopier le mot pour valider l'opération",
        },
    )

    convention = forms.CharField(widget=forms.HiddenInput())

    def submit(self, request):
        convention = Convention.objects.get(pk=self.cleaned_data["convention"])
        new_administration = self.cleaned_data["administration"]
        avenants_to_updates = convention.avenants.all()
        conventions_to_update = [convention, *avenants_to_updates]

        Programme.objects.filter(conventions__in=conventions_to_update).update(
            administration=new_administration
        )

        messages.success(
            request,
            "L'administration a été modifiée avec succès. "
            f"Nouvelle administration : {new_administration.nom}.",
        )

        return redirect("conventions:search_instruction")
