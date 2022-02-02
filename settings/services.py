from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from users.forms import UserForm
from instructeurs.models import Administration
from instructeurs.forms import AdministrationForm


@login_required
def user_profile(request):
    # display user form
    success = False
    if request.method == "POST":
        posted_request = request.POST.dict()
        posted_request["username"] = request.user.username
        userform = UserForm(posted_request)
        if userform.is_valid():
            request.user.first_name = userform.cleaned_data["first_name"]
            request.user.last_name = userform.cleaned_data["last_name"]
            request.user.email = userform.cleaned_data["email"]
            request.user.save()
            success = True
    else:
        userform = UserForm(initial=model_to_dict(request.user))
    return {
        "form": userform,
        "editable": True,
        "success": success,
    }


@login_required
def user_list(request):

    my_user_list = request.user.user_list()
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
def administration_list(request):

    my_administration_list = request.user.administrations()
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
        form = AdministrationForm(request.POST)
        if form.is_valid():
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


@login_required
def bailleur_list(request):

    my_bailleur_list = request.user.bailleurs()
    page = request.GET.get("page", 1)
    paginator = Paginator(my_bailleur_list, 20)
    try:
        bailleurs = paginator.page(page)
    except PageNotAnInteger:
        bailleurs = paginator.page(1)
    except EmptyPage:
        bailleurs = paginator.page(paginator.num_pages)

    return {"bailleurs": bailleurs}
