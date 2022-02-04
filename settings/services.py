from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from bailleurs.forms import BailleurForm
from bailleurs.models import Bailleur
from conventions.services import utils
from instructeurs.forms import AdministrationForm
from instructeurs.models import Administration
from users.forms import UserForm
from users.models import User


@login_required
def user_profile(request):
    # display user form
    success = False
    if request.method == "POST":
        posted_request = request.POST.dict()
        posted_request["username"] = request.user.username
        # Erase admnistrateur de compte if current user is not admin
        # Because a non-administrator can't give this status himself
        userform = UserForm(
            {
                **request.POST.dict(),
                "username": request.user.username,
                "administrateur_de_compte": (
                    request.POST.get("administrateur_de_compte", False)
                    if request.user.is_administrator()
                    else request.user.administrateur_de_compte
                ),
            }
        )
        if userform.is_valid():
            request.user.first_name = userform.cleaned_data["first_name"]
            request.user.last_name = userform.cleaned_data["last_name"]
            request.user.email = userform.cleaned_data["email"]
            request.user.administrateur_de_compte = userform.cleaned_data[
                "administrateur_de_compte"
            ]
            request.user.save()
            success = True
    else:
        userform = UserForm(initial=model_to_dict(request.user))
    return {
        "form": userform,
        "editable": True,
        "success": success,
    }


@require_GET
@login_required
def administration_list(request):

    my_administration_list = request.user.administrations().order_by("nom")
    page = request.GET.get("page", 1)
    paginator = Paginator(my_administration_list, 20)
    try:
        administrations = paginator.page(page)
    except PageNotAnInteger:
        administrations = paginator.page(1)
    except EmptyPage:
        administrations = paginator.page(paginator.num_pages)

    return {"administrations": administrations}


@login_required
def edit_administration(request, administration_uuid):
    administration = Administration.objects.get(uuid=administration_uuid)
    success = False
    if request.method == "POST":
        form = AdministrationForm({**request.POST.dict(), "uuid": administration_uuid})
        if form.is_valid():
            administration.nom = form.cleaned_data["nom"]
            administration.code = form.cleaned_data["code"]
            administration.ville_signature = form.cleaned_data["ville_signature"]
            administration.save()
            success = True
    else:
        form = AdministrationForm(initial=model_to_dict(administration))
    return {
        "form": form,
        "editable": True,
        "success": success,
    }


@require_GET
@login_required
def bailleur_list(request):

    my_bailleur_list = request.user.bailleurs().order_by("nom")
    page = request.GET.get("page", 1)
    paginator = Paginator(my_bailleur_list, 20)
    try:
        bailleurs = paginator.page(page)
    except PageNotAnInteger:
        bailleurs = paginator.page(1)
    except EmptyPage:
        bailleurs = paginator.page(paginator.num_pages)

    return {"bailleurs": bailleurs}


@login_required
def edit_bailleur(request, bailleur_uuid):
    bailleur = Bailleur.objects.get(uuid=bailleur_uuid)
    success = False
    if request.method == "POST":
        form = BailleurForm({**request.POST.dict(), "uuid": bailleur_uuid})
        if form.is_valid():
            bailleur.nom = form.cleaned_data["nom"]
            bailleur.siret = form.cleaned_data["siret"]
            bailleur.capital_social = form.cleaned_data["capital_social"]
            bailleur.adresse = form.cleaned_data["adresse"]
            bailleur.code_postal = form.cleaned_data["code_postal"]
            bailleur.ville = form.cleaned_data["ville"]
            bailleur.signataire_nom = form.cleaned_data["signataire_nom"]
            bailleur.signataire_fonction = form.cleaned_data["signataire_fonction"]
            bailleur.signataire_date_deliberation = form.cleaned_data[
                "signataire_date_deliberation"
            ]
            bailleur.save()
            success = True
    else:
        form = BailleurForm(
            initial={
                **model_to_dict(
                    bailleur,
                    fields=[
                        "uuid",
                        "nom",
                        "siret",
                        "capital_social",
                        "adresse",
                        "code_postal",
                        "ville",
                        "signataire_nom",
                        "signataire_fonction",
                    ],
                ),
                "signataire_date_deliberation": utils.format_date_for_form(
                    bailleur.signataire_date_deliberation
                ),
            }
        )
    return {
        "form": form,
        "editable": True,
        "success": success,
    }


@require_GET
@login_required
def user_list(request):

    my_user_list = request.user.user_list().order_by("username")
    page = request.GET.get("page", 1)
    paginator = Paginator(my_user_list, 20)
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    return {"users": users}


@login_required
def edit_user(request, username):
    user = User.objects.get(username=username)
    success = False
    if request.method == "POST" and request.user.is_administrator(user):
        # Erase admnistrateur de compte if current user is not admin
        # Because a non-administrator can't give this status himself
        # --> need to chack the common scope of user and current user
        form = UserForm(
            {
                **request.POST.dict(),
                "username": username,
                "administrateur_de_compte": (
                    request.POST.get("administrateur_de_compte", False)
                    if request.user.is_administrator(user)
                    else user.administrateur_de_compte
                ),
                "is_superuser": (
                    request.POST.get("is_superuser", False)
                    if request.user.is_superuser
                    else user.is_superuser
                ),
            }
        )

        if form.is_valid():
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            user.administrateur_de_compte = form.cleaned_data[
                "administrateur_de_compte"
            ]
            user.is_superuser = form.cleaned_data["is_superuser"]
            user.save()
            success = True
    else:
        form = UserForm(initial=model_to_dict(user))
    return {
        "form": form,
        "user": user,
        "editable": True,
        "success": success,
    }


@require_POST
@login_required
def add_user_bailleur(request, username):
    user = User.objects.get(username=username)
    return {"user": user, "success": True}
