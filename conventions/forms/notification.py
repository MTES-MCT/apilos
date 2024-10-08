from django import forms


class NotificationForm(forms.Form):

    send_copy = forms.BooleanField(required=False)
    from_instructeur = forms.BooleanField(required=False)
    comment = forms.CharField(
        required=False,
        label="Ajouter un commentaire à l'attention du bailleur (optionnel)",
        max_length=5000,
        error_messages={
            "max_length": "Le commentaire ne doit pas excéder 5000 caractères",
        },
    )
