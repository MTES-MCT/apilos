from django.shortcuts import render
from bailleurs.models import Bailleur


def bailleur_signataire(request, nom):
    bailleur = Bailleur.objects.get(nom=nom)
    signataires = bailleur.signataires_set.all()
    return render(
        request,
        "settings/signataire.html",
        {**signataires},
    )
