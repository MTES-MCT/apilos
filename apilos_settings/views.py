from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.forms import model_to_dict
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET, require_http_methods
from django.views.generic.edit import FormView

from apilos_settings import services
from bailleurs.models import Bailleur
from conventions.forms import BailleurForm
from conventions.services import utils
from instructeurs.forms import AdministrationForm
from instructeurs.models import Administration
from users.forms import UserNotificationForm
from users.models import User


@require_GET
@login_required
def administrations(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "settings/administrations.html",
        services.administration_list(request),
    )


@require_GET
@login_required
def bailleurs(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "settings/bailleurs.html",
        services.bailleur_list(request),
    )


@require_http_methods(["GET", "POST"])
@login_required
def profile(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UserNotificationForm(request.POST)
        if form.is_valid() and form.cleaned_data["preferences_email"] is not None:
            request.user.preferences_email = form.cleaned_data["preferences_email"]
            request.user.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                "Votre profil a été enregistré avec succès",
            )
    else:
        form = UserNotificationForm(
            initial={"preferences_email": request.user.preferences_email}
        )

    return render(
        request,
        "settings/user_profile.html",
        {
            "form": form,
        },
    )


@require_GET
@login_required
def users(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "settings/users.html",
        services.user_list(request),
    )


class EditBailleurView(LoginRequiredMixin, FormView):
    template_name = "settings/edit_bailleur.html"
    form_class = BailleurForm

    def _get_bailleur(self, bailleur_uuid):
        try:
            return self.request.user.bailleurs(full_scope=True).get(uuid=bailleur_uuid)
        except Bailleur.DoesNotExist as e:
            raise PermissionDenied(
                "Vous n'avez pas les droits pour accéder à ce bailleur"
            ) from e

    def get_success_url(self):
        return reverse_lazy(
            "settings:edit_bailleur",
            kwargs={"bailleur_uuid": self.kwargs["bailleur_uuid"]},
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        bailleur = self._get_bailleur(self.kwargs["bailleur_uuid"])
        kwargs.update(
            {
                "initial": {
                    **model_to_dict(
                        bailleur,
                        fields=[
                            "uuid",
                            "nature_bailleur",
                            "sous_nature_bailleur",
                            "nom",
                            "siret",
                            "siren",
                            "capital_social",
                            "adresse",
                            "code_postal",
                            "ville",
                            "signataire_nom",
                            "signataire_fonction",
                            "signataire_bloc_signature",
                        ],
                    ),
                    "bailleur": bailleur.parent if bailleur.parent else "",
                    "signataire_date_deliberation": utils.format_date_for_form(
                        bailleur.signataire_date_deliberation
                    ),
                },
                "bailleur_query": self.request.user.bailleur_query_set(
                    only_bailleur_uuid=(
                        bailleur.parent.uuid if bailleur.parent else None
                    ),
                    exclude_bailleur_uuid=bailleur.uuid,
                    has_no_parent=True,
                ),
            }
        )
        return kwargs

    def post(self, request, *args, **kwargs):
        bailleur = self._get_bailleur(self.kwargs["bailleur_uuid"])
        form = self.form_class(
            {
                **request.POST.dict(),
                "uuid": bailleur.uuid,
                "siren": bailleur.siren,
                "sous_nature_bailleur": (
                    request.POST.get("sous_nature_bailleur")
                    if self.request.user.is_admin
                    else bailleur.sous_nature_bailleur
                ),
                "nature_bailleur": (
                    request.POST.get("nature_bailleur")
                    if self.request.user.is_admin
                    else bailleur.nature_bailleur
                ),
            },
            bailleur_query=request.user.bailleur_query_set(
                only_bailleur_uuid=request.POST.get("bailleur")
            ),
        )
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        bailleur = self._get_bailleur(self.kwargs["bailleur_uuid"])
        bailleur.nature_bailleur = form.cleaned_data["nature_bailleur"]
        bailleur.sous_nature_bailleur = form.cleaned_data["sous_nature_bailleur"]
        bailleur.nom = form.cleaned_data["nom"]
        bailleur.parent = (
            form.cleaned_data["bailleur"] if form.cleaned_data["bailleur"] else None
        )
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
        bailleur.signataire_bloc_signature = form.cleaned_data[
            "signataire_bloc_signature"
        ]
        bailleur.save()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "L'entité bailleur a été enregistrée avec succès",
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bailleur"] = Bailleur.objects.get(uuid=self.kwargs["bailleur_uuid"])
        context["editable"] = True
        return context


class EditAdministrationView(FormView):
    template_name = "settings/edit_administration.html"
    form_class = AdministrationForm

    def _get_administration(self, administration_uuid):
        try:
            return self.request.user.administrations(full_scope=True).get(
                uuid=administration_uuid
            )
        except Administration.DoesNotExist as e:
            raise PermissionDenied(
                "Vous n'avez pas les droits pour accéder à ce bailleur"
            ) from e

    def get_initial(self):
        administration = self._get_administration(self.kwargs["administration_uuid"])
        return model_to_dict(administration)

    def form_valid(self, form):
        administration = self._get_administration(self.kwargs["administration_uuid"])
        administration.nom = form.cleaned_data["nom"]
        administration.code = form.cleaned_data["code"]
        administration.ville_signature = form.cleaned_data["ville_signature"]
        administration.adresse = form.cleaned_data["adresse"]
        administration.code_postal = form.cleaned_data["code_postal"]
        administration.ville = form.cleaned_data["ville"]
        administration.signataire_bloc_signature = form.cleaned_data[
            "signataire_bloc_signature"
        ]
        administration.nb_convention_exemplaires = form.cleaned_data[
            "nb_convention_exemplaires"
        ]
        administration.save()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "L'administration a été enregistrée avec succès",
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        administration = self._get_administration(self.kwargs["administration_uuid"])
        user_list_service = services.UserListService(
            search_input=self.request.GET.get("search_input", ""),
            order_by=self.request.GET.get("order_by", "username"),
            page=self.request.GET.get("page", 1),
            my_user_list=User.objects.filter(
                roles__in=administration.roles.all()
            ).distinct(),
        )
        user_list_service.paginate()
        context.update(user_list_service.as_dict())
        context["editable"] = True
        return context

    def get_success_url(self):
        return reverse_lazy(
            "settings:edit_administration",
            kwargs={"administration_uuid": self.kwargs["administration_uuid"]},
        )

    def post(self, request, *args, **kwargs):
        administration = Administration.objects.get(
            uuid=self.kwargs["administration_uuid"]
        )
        form = self.form_class(
            {
                **request.POST.dict(),
                "uuid": administration.uuid,
                "nom": request.POST.get("nom", administration.nom),
                "code": administration.code,
            }
        )
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class UserProfileView(FormView):
    template_name = "settings/user_profile.html"
    form_class = UserNotificationForm
    success_url = reverse_lazy("settings:profile")

    def get_initial(self):
        return {"preferences_email": self.request.user.preferences_email}

    def form_valid(self, form):
        self.request.user.preferences_email = form.cleaned_data["preferences_email"]
        self.request.user.save()
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Votre profil a été enregistré avec succès",
        )
        return super().form_valid(form)
