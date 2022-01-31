from django import forms


class UserForm(forms.Form):
    username = forms.CharField(
        required=True,
        max_length=150,
        min_length=1,
        error_messages={
            "required": "Le nom d'utilisateur est obligatoire",
            "min_length": "Le nom d'utilisateur est obligatoire",
            "max_length": "Le nom du programme ne doit pas excéder 150 caractères",
        },
    )

    first_name = forms.CharField(
        required=False,
        max_length=150,
        error_messages={
            "max_length": "Le nom du programme ne doit pas excéder 150 caractères",
        },
    )

    last_name = forms.CharField(
        required=False,
        max_length=150,
        error_messages={
            "max_length": "Le nom du programme ne doit pas excéder 150 caractères",
        },
    )

    email = forms.EmailField(
        required=True,
        error_messages={
            "required": "Le nom d'utilisateur est obligatoire",
        },
    )
