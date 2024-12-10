from django import forms


class UploadForm(forms.Form):

    file = forms.FileField(
        error_messages={
            "required": (
                "Vous devez sélectionner un fichier avant "
                + "de cliquer sur le bouton 'Déposer'"
            ),
        }
    )