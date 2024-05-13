from typing import Any

from django.conf import settings
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpRequest
from django.views.decorators.http import require_GET

from bailleurs.models import Bailleur
from conventions.forms import BailleurForm
from conventions.services import utils
from instructeurs.forms import AdministrationForm
from instructeurs.models import Administration
from users.forms import UserNotificationForm
from users.models import User


def user_is_staff_or_admin(request: HttpRequest) -> bool:
    return request.user.is_superuser or request.user.is_staff


def user_profile(request: HttpRequest) -> dict[str, Any]:
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

    return {
        "form": form,
        "editable": True,
        "user_is_staff_or_admin": user_is_staff_or_admin(request),
    }


@require_GET
def administration_list(request: HttpRequest) -> dict[str, Any]:
    search_input = request.GET.get("search_input", "")
    order_by = request.GET.get("order_by", "nom")
    page = request.GET.get("page", 1)

    my_administration_list = (
        Administration.objects.all().order_by(order_by)
        if user_is_staff_or_admin(request)
        else request.user.administrations().order_by(order_by)
    )
    total_administration = my_administration_list.count()
    if search_input:
        my_administration_list = my_administration_list.filter(
            Q(nom__icontains=search_input)
            | Q(code__icontains=search_input)
            | Q(ville_signature__icontains=search_input)
        )

    paginator = Paginator(my_administration_list, settings.APILOS_PAGINATION_PER_PAGE)
    try:
        administrations = paginator.page(page)
    except PageNotAnInteger:
        administrations = paginator.page(1)
    except EmptyPage:
        page = paginator.num_pages
        administrations = paginator.page(page)

    return {
        "administrations": administrations,
        "total_administration": total_administration,
        "order_by": order_by,
        "search_input": search_input,
        "user_is_staff_or_admin": user_is_staff_or_admin(request),
    }


def edit_administration(request, administration_uuid):
    administration = Administration.objects.get(uuid=administration_uuid)
    success = False
    if request.method == "POST":
        form = AdministrationForm(
            {
                **request.POST.dict(),
                "uuid": administration_uuid,
                "nom": request.POST.get("nom", administration.nom),
                "code": (
                    request.POST.get("code", False)
                    if user_is_staff_or_admin(request)
                    else administration.code
                ),
            }
        )
        if form.is_valid():
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
                request,
                messages.SUCCESS,
                "L'administration a été enregistrée avec succès",
            )
            success = True
    else:
        form = AdministrationForm(initial=model_to_dict(administration))

    user_list_service = UserListService(
        search_input=request.GET.get("search_input", ""),
        order_by=request.GET.get("order_by", "username"),
        page=request.GET.get("page", 1),
        my_user_list=User.objects.filter(
            roles__in=administration.roles.all()
        ).distinct(),
    )
    user_list_service.paginate()

    return {
        **user_list_service.as_dict(),
        "form": form,
        "editable": True,
        "success": success,
        "user_is_staff_or_admin": user_is_staff_or_admin(request),
    }


@require_GET
def bailleur_list(request: HttpRequest) -> dict[str, Any]:
    bailleur_list_service = BailleurListService(
        search_input=request.GET.get("search_input", ""),
        order_by=request.GET.get("order_by", "nom"),
        page=request.GET.get("page", 1),
        item_list=(
            Bailleur.objects.all().order_by("nom")
            if user_is_staff_or_admin(request)
            else request.user.bailleurs()
        ),
    )
    bailleur_list_service.paginate()
    return {
        "user_is_staff_or_admin": user_is_staff_or_admin(request),
        **bailleur_list_service.as_dict(),
    }


def edit_bailleur(request, bailleur_uuid):
    bailleur = Bailleur.objects.get(uuid=bailleur_uuid)
    success = False
    if request.method == "POST":
        form = BailleurForm(
            {
                **request.POST.dict(),
                "uuid": bailleur_uuid,
                "siren": bailleur.siren,
                "sous_nature_bailleur": (
                    request.POST.get("sous_nature_bailleur")
                    if user_is_staff_or_admin(request)
                    else bailleur.sous_nature_bailleur
                ),
                "nature_bailleur": (
                    request.POST.get("nature_bailleur")
                    if user_is_staff_or_admin(request)
                    else bailleur.nature_bailleur
                ),
            },
            bailleur_query=request.user.bailleur_query_set(
                only_bailleur_uuid=request.POST.get("bailleur")
            ),
        )
        if form.is_valid():
            if user_is_staff_or_admin(request):
                parent = (
                    form.cleaned_data["bailleur"]
                    if form.cleaned_data["bailleur"]
                    else None
                )
            else:
                parent = bailleur.parent
            bailleur.nature_bailleur = form.cleaned_data["nature_bailleur"]
            bailleur.sous_nature_bailleur = form.cleaned_data["sous_nature_bailleur"]
            bailleur.nom = form.cleaned_data["nom"]
            bailleur.parent = parent
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
                request,
                messages.SUCCESS,
                "L'entité bailleur a été enregistrée avec succès",
            )
    else:
        form = BailleurForm(
            initial={
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
            bailleur_query=request.user.bailleur_query_set(
                only_bailleur_uuid=bailleur.parent.uuid if bailleur.parent else None,
                exclude_bailleur_uuid=bailleur.uuid,
                has_no_parent=True,
            ),
        )
    user_list_service = UserListService(
        search_input=request.GET.get("search_input", ""),
        order_by=request.GET.get("order_by", "username"),
        page=request.GET.get("page", 1),
        my_user_list=User.objects.filter(roles__in=bailleur.roles.all()).distinct(),
    )
    user_list_service.paginate()

    return {
        "user_list": user_list_service,
        "bailleur": bailleur,
        "form": form,
        "editable": True,
        "success": success,
        "user_is_staff_or_admin": user_is_staff_or_admin(request),
    }


@require_GET
def user_list(request: HttpRequest) -> dict[str, Any]:
    user_list_service = UserListService(
        search_input=request.GET.get("search_input", ""),
        order_by=request.GET.get("order_by", "username"),
        page=request.GET.get("page", 1),
        my_user_list=(
            User.objects.exclude(Q(is_staff=True) | Q(is_superuser=True))
            if user_is_staff_or_admin(request)
            else request.user.user_list()
        ),
    )
    user_list_service.paginate()
    return {
        "user_is_staff_or_admin": user_is_staff_or_admin(request),
        **user_list_service.as_dict(),
    }


class UserListService:
    search_input: str
    order_by: str
    page: str
    my_user_list: Any
    paginated_users: Any
    total_users: int

    def __init__(
        self,
        search_input: str,
        order_by: str,
        page: str,
        my_user_list: Any,
    ):
        self.search_input = search_input
        self.order_by = order_by
        self.page = page
        self.my_user_list = my_user_list

    def paginate(self) -> None:
        total_user = self.my_user_list.count()
        if self.search_input:
            self.my_user_list = self.my_user_list.filter(
                Q(username__icontains=self.search_input)
                | Q(first_name__icontains=self.search_input)
                | Q(last_name__icontains=self.search_input)
                | Q(email__icontains=self.search_input)
            )
        if self.order_by:
            self.my_user_list = self.my_user_list.order_by(self.order_by)

        paginator = Paginator(self.my_user_list, settings.APILOS_PAGINATION_PER_PAGE)
        try:
            users = paginator.page(self.page)
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        self.paginated_users = users
        self.total_users = total_user

    def as_dict(self):
        return {
            "search_input": self.search_input,
            "order_by": self.order_by,
            "page": self.page,
            "my_user_list": self.my_user_list,
            "paginated_users": self.paginated_users,
            "total_users": self.total_users,
        }


class ListService:
    search_input: str
    order_by: str
    page: str
    item_list: Any
    paginated_items: Any
    total_items: int

    def __init__(
        self,
        search_input: str,
        order_by: str,
        page: str,
        item_list: Any,
    ):
        self.search_input = search_input
        self.order_by = order_by
        self.page = page
        self.item_list = item_list

    def _get_filter(self):
        pass

    def paginate(self) -> None:
        total_items = self.item_list.count()
        if self.search_input:
            self.item_list = self.item_list.filter(self._get_filter())
        if self.order_by:
            self.item_list = self.item_list.order_by(self.order_by)

        paginator = Paginator(self.item_list, settings.APILOS_PAGINATION_PER_PAGE)
        try:
            items = paginator.page(self.page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)

        self.paginated_items = items
        self.total_items = total_items

    def as_dict(self):
        return {
            "search_input": self.search_input,
            "order_by": self.order_by,
            "page": self.page,
            "item_list": self.item_list,
            "paginated_items": self.paginated_items,
            "total_items": self.total_items,
        }


class BailleurListService(ListService):
    def _get_filter(self):
        return (
            Q(nom__icontains=self.search_input)
            | Q(siret__icontains=self.search_input)
            | Q(ville__icontains=self.search_input)
        )
