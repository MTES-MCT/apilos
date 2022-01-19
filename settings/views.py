from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.


def profile(request):
    # display user form
    return render(request, "settings/user_profile.html")


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
