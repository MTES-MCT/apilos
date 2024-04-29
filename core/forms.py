from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Votre nom complet", "class": "fr-input"}
        ),
        max_length=100,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": "Votre adresse email", "class": "fr-input"}
        )
    )
    subject = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Sujet du message", "class": "fr-input"}
        )
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "Votre message", "class": "fr-input"}
        ),
        label="Message",
        help_text="Expliquez nous en quelques mots votre cas d'usage",
        required=True,
        error_messages={
            "required": "Votre message est obligatoire",
        },
    )
