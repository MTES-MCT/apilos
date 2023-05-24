from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from users.models import User


class MockedCerbereLoginView(View):
    def get(self, request):
        return render(request, "cerbere/login.html")

    def post(self, request):
        user = User.objects.filter(cerbere_login=request.POST.get("login")).first()

        if user and user.is_cerbere_user():
            return redirect(
                reverse("cas_ng_login") + "?ticket=" + user.cerbere_login + "&next=/"
            )

        return render(request, "cerbere/login.html", {"user": user})
