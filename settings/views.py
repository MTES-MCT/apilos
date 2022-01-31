from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required

from users.forms import UserForm


@login_required
def profile(request):
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
        print("update user")
    else:
        userform = UserForm(initial=model_to_dict(request.user))
    return render(
        request,
        "settings/user_profile.html",
        {
            "form": userform,
            "editable": True,
            "success": success,
        },
    )


def index(request):
    if request.user.is_bailleur():
        return HttpResponseRedirect(reverse("settings:bailleurs"))
    if request.user.is_instructeur():
        return HttpResponseRedirect(reverse("settings:instructeurs"))
    return HttpResponseRedirect(reverse("settings:users"))


def users(request):
    return render(request, "settings/users.html")


def bailleurs(request):
    return render(request, "settings/bailleurs.html")


def administrations(request):
    return render(request, "settings/administrations.html")
