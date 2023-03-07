from typing import Any

from django.contrib import messages
from django.http import HttpRequest
from django.forms.models import model_to_dict
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import Group


from apilos_settings.forms import BailleurListingUploadForm
from conventions.forms import BailleurForm
from bailleurs.models import Bailleur, NatureBailleur
from conventions.services import utils
from conventions.services.utils import ReturnStatus
from core.services import EmailService, EmailTemplateID
from instructeurs.forms import AdministrationForm
from instructeurs.models import Administration
from users.forms import AddAdministrationForm, AddBailleurForm, AddUserForm, UserForm
from users.models import User, Role, TypeRole
from users.forms import UserBailleurFormSet
from users.services import UserService


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
                "is_superuser": (
                    request.POST.get("is_superuser", False)
                    if request.user.is_superuser
                    else request.user.is_superuser
                ),
                "filtre_departements": (
                    [int(num) for num in request.POST["filtre_departements"].split(",")]
                    if "filtre_departements" in request.POST
                    and request.POST["filtre_departements"]
                    else []
                ),
            }
        )
        if userform.is_valid():
            request.user.email = userform.cleaned_data["email"]
            request.user.first_name = userform.cleaned_data["first_name"]
            request.user.last_name = userform.cleaned_data["last_name"]
            request.user.telephone = userform.cleaned_data["telephone"]
            if userform.cleaned_data["preferences_email"] is not None:
                request.user.preferences_email = userform.cleaned_data[
                    "preferences_email"
                ]
            request.user.administrateur_de_compte = userform.cleaned_data[
                "administrateur_de_compte"
            ]
            request.user.is_superuser = userform.cleaned_data["is_superuser"]
            request.user.save()
            if userform.cleaned_data["filtre_departements"] is not None:
                request.user.filtre_departements.clear()
                request.user.filtre_departements.add(
                    *userform.cleaned_data["filtre_departements"]
                )
            success = True
    else:
        userform = UserForm(initial=model_to_dict(request.user))

    return {
        "form": userform,
        "editable": True,
        "success": success,
    }


@require_GET
def administration_list(request):
    search_input = request.GET.get("search_input", "")
    order_by = request.GET.get("order_by", "nom")
    page = request.GET.get("page", 1)

    my_administration_list = request.user.administrations().order_by(order_by)
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
    }


def edit_administration(request, administration_uuid):
    administration = Administration.objects.get(uuid=administration_uuid)
    success = False
    if request.method == "POST":
        form = AdministrationForm(
            {
                **request.POST.dict(),
                "uuid": administration_uuid,
                "code": (
                    request.POST.get("code", False)
                    if request.user.is_superuser
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
            administration.prefix_convention = form.cleaned_data["prefix_convention"]
            administration.save()
            success = True
    else:
        form = AdministrationForm(initial=model_to_dict(administration))

    user_list_service = UserListService(
        search_input=request.GET.get("search_input", ""),
        order_by=request.GET.get("order_by", "username"),
        page=request.GET.get("page", 1),
        my_user_list=User.objects.filter(roles__in=administration.roles.all()),
    )
    user_list_service.paginate()

    return {
        **user_list_service.as_dict(),
        "form": form,
        "editable": True,
        "success": success,
    }


def edit_bailleur(request, bailleur_uuid):
    bailleur = Bailleur.objects.get(uuid=bailleur_uuid)
    success = False
    if request.method == "POST":
        form = BailleurForm(
            {
                **request.POST.dict(),
                "uuid": bailleur_uuid,
                "sous_nature_bailleur": (
                    request.POST.get("sous_nature_bailleur", False)
                    if request.user.is_superuser
                    else bailleur.sous_nature_bailleur
                ),
            },
            bailleurs=[
                (b.uuid, b.nom)
                for b in request.user.bailleurs(full_scope=True)
                .exclude(id=bailleur.id)
                .filter(parent_id__isnull=True)
            ],
        )
        if form.is_valid():
            if request.user.is_superuser or request.user.administrateur_de_compte:
                parent = (
                    Bailleur.objects.get(uuid=form.cleaned_data["bailleur"])
                    if form.cleaned_data["bailleur"]
                    else None
                )
            else:
                parent = bailleur.parent
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
            success = True
    else:
        form = BailleurForm(
            initial={
                **model_to_dict(
                    bailleur,
                    fields=[
                        "uuid",
                        "sous_nature_bailleur",
                        "nom",
                        "siret",
                        "capital_social",
                        "adresse",
                        "code_postal",
                        "ville",
                        "signataire_nom",
                        "signataire_fonction",
                        "signataire_bloc_signature",
                    ],
                ),
                "bailleur": bailleur.parent.uuid if bailleur.parent else None,
                "signataire_date_deliberation": utils.format_date_for_form(
                    bailleur.signataire_date_deliberation
                ),
            },
            bailleurs=[
                (b.uuid, b.nom)
                for b in request.user.bailleurs(full_scope=True)
                .exclude(id=bailleur.id)
                .filter(parent_id__isnull=True)
            ],
        )
    user_list_service = UserListService(
        search_input=request.GET.get("search_input", ""),
        order_by=request.GET.get("order_by", "username"),
        page=request.GET.get("page", 1),
        my_user_list=User.objects.filter(roles__in=bailleur.roles.all()),
    )
    user_list_service.paginate()

    return {
        "user_list": user_list_service,
        "bailleur": bailleur,
        "form": form,
        "editable": True,
        "success": success,
    }


@require_GET
def user_list(request):

    user_list_service = UserListService(
        search_input=request.GET.get("search_input", ""),
        order_by=request.GET.get("order_by", "username"),
        page=request.GET.get("page", 1),
        my_user_list=request.user.user_list(),
    )
    user_list_service.paginate()

    return user_list_service.as_dict()


def edit_user(request, username):
    user = User.objects.get(username=username)
    status = ""
    bailleurs = [
        (b.uuid, b.nom)
        for b in request.user.bailleurs(full_scope=True).exclude(
            nature_bailleur=NatureBailleur.PRIVES
        )
    ]
    administrations = [
        (b.uuid, b.nom) for b in request.user.administrations(full_scope=True)
    ]
    if request.method == "POST" and request.user.is_administrator(user):

        action_type = request.POST.get("action_type", "")
        if action_type == "remove_bailleur":
            form = UserForm(initial=model_to_dict(user))
            form_add_bailleur = AddBailleurForm(bailleurs=bailleurs)
            form_add_administration = AddAdministrationForm(
                administrations=administrations
            )
            bailleur_uuid = request.POST.get("bailleur")
            Role.objects.get(
                typologie=TypeRole.BAILLEUR,
                bailleur=request.user.bailleurs().get(uuid=bailleur_uuid),
                user=user,
            ).delete()
        elif action_type == "add_bailleur":
            form = UserForm(initial=model_to_dict(user))
            form_add_administration = AddAdministrationForm(
                administrations=administrations
            )
            form_add_bailleur = AddBailleurForm(request.POST, bailleurs=bailleurs)
            if form_add_bailleur.is_valid() and request.user.is_administrator():
                Role.objects.create(
                    typologie=TypeRole.BAILLEUR,
                    bailleur=request.user.bailleurs().get(
                        uuid=form_add_bailleur.cleaned_data["bailleur"]
                    ),
                    user=user,
                    group=Group.objects.get(name="bailleur"),
                )
        elif action_type == "remove_administration":
            form = UserForm(initial=model_to_dict(user))
            form_add_bailleur = AddBailleurForm(bailleurs=bailleurs)
            form_add_administration = AddAdministrationForm(
                administrations=administrations
            )
            administration_uuid = request.POST.get("administration")
            Role.objects.get(
                typologie=TypeRole.INSTRUCTEUR,
                administration=request.user.administrations().get(
                    uuid=administration_uuid
                ),
                user=user,
            ).delete()
        elif action_type == "add_administration":
            form = UserForm(initial=model_to_dict(user))
            form_add_bailleur = AddBailleurForm(bailleurs=bailleurs)
            form_add_administration = AddAdministrationForm(
                request.POST, administrations=administrations
            )
            if form_add_administration.is_valid() and request.user.is_administrator():
                Role.objects.create(
                    typologie=TypeRole.INSTRUCTEUR,
                    administration=request.user.administrations().get(
                        uuid=form_add_administration.cleaned_data["administration"]
                    ),
                    user=user,
                    group=Group.objects.get(name="instructeur"),
                )
        else:
            form_add_bailleur = AddBailleurForm(bailleurs=bailleurs)
            form_add_administration = AddAdministrationForm(
                administrations=administrations
            )
            # Erase admnistrateur de compte if current user is not admin
            # Because a non-administrator can't give this status himself
            # --> need to check the common scope of user and current user
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
                    # Without virtualselect, we have a list of strings
                    # "filtre_departements": request.POST.getlist("filtre_departements"),
                    # With virtualselect, we have a string of comma separated values
                    "filtre_departements": (
                        [num for num in request.POST["filtre_departements"].split(",")]
                        if "filtre_departements" in request.POST
                        and request.POST["filtre_departements"]
                        else []
                    ),
                }
            )

            if form.is_valid():
                user.email = form.cleaned_data["email"]
                user.first_name = form.cleaned_data["first_name"]
                user.last_name = form.cleaned_data["last_name"]
                user.telephone = form.cleaned_data["telephone"]
                if form.cleaned_data["preferences_email"] is not None:
                    user.preferences_email = form.cleaned_data["preferences_email"]
                user.administrateur_de_compte = form.cleaned_data[
                    "administrateur_de_compte"
                ]
                user.is_superuser = form.cleaned_data["is_superuser"]
                user.save()
                user.filtre_departements.clear()
                for departement in form.cleaned_data["filtre_departements"]:
                    user.filtre_departements.add(departement)
                status = "user_updated"
    else:
        (form, form_add_bailleur, form_add_administration) = _init_user_form(
            user, bailleurs=bailleurs, administrations=administrations
        )
    return {
        "form": form,
        "user": user,
        "editable": True,
        "status": status,
        "form_add_bailleur": form_add_bailleur,
        "form_add_administration": form_add_administration,
    }


def _init_user_form(user, bailleurs=None, administrations=None):
    return (
        UserForm(
            initial={
                **model_to_dict(user),
                "filtre_departements": user.filtre_departements.all(),
            }
        ),
        AddBailleurForm(bailleurs=bailleurs),
        AddAdministrationForm(administrations=administrations),
    )


def add_user(request):
    status = ""
    bailleurs = [
        (b.uuid, b.nom)
        for b in request.user.bailleurs(full_scope=True).exclude(
            nature_bailleur=NatureBailleur.PRIVES
        )
    ]
    administrations = [
        (b.uuid, b.nom) for b in request.user.administrations(full_scope=True)
    ]
    if request.method == "POST" and request.user.is_administrator():
        form = AddUserForm(
            {
                **request.POST.dict(),
                "filtre_departements": (
                    [int(num) for num in request.POST["filtre_departements"].split(",")]
                    if "filtre_departements" in request.POST
                    and request.POST["filtre_departements"]
                    else []
                ),
            },
            bailleurs=bailleurs,
            administrations=administrations,
        )
        if form.is_valid():
            # Forbid non super users to grant super user role to new users
            is_superuser = (
                form.cleaned_data["is_superuser"]
                if request.user.is_superuser
                else False
            )
            user = User.objects.create(
                email=form.cleaned_data["email"],
                username=form.cleaned_data["username"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                telephone=form.cleaned_data["telephone"],
                administrateur_de_compte=form.cleaned_data["administrateur_de_compte"],
                is_superuser=is_superuser,
                creator=request.user,
            )
            if form.cleaned_data["preferences_email"] is not None:
                user.preferences_email = form.cleaned_data["preferences_email"]

            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            if form.cleaned_data["filtre_departements"] is not None:
                user.filtre_departements.clear()
                user.filtre_departements.add(*form.cleaned_data["filtre_departements"])
            if form.cleaned_data["user_type"] == "BAILLEUR":
                EmailService(
                    to_emails=[user.email],
                    email_template_id=EmailTemplateID.B_WELCOME,
                ).send_transactional_email(
                    email_data={
                        "email": user.email,
                        "username": user.username,
                        "firstname": user.first_name,
                        "lastname": user.last_name,
                        "password": password,
                        "login_url": request.build_absolute_uri("/accounts/login/"),
                    }
                )
                Role.objects.create(
                    typologie=TypeRole.BAILLEUR,
                    bailleur=request.user.bailleurs().get(
                        uuid=form.cleaned_data["bailleur"]
                    ),
                    user=user,
                    group=Group.objects.get(name="bailleur"),
                )
            if form.cleaned_data["user_type"] == "INSTRUCTEUR":
                EmailService(
                    to_emails=[user.email],
                    email_template_id=EmailTemplateID.I_WELCOME,
                ).send_transactional_email(
                    email_data={
                        "email": user.email,
                        "username": user.username,
                        "firstname": user.first_name,
                        "lastname": user.last_name,
                        "password": password,
                        "login_url": request.build_absolute_uri("/accounts/login/")
                        + "?instructeur=1",
                    }
                )
                Role.objects.create(
                    typologie=TypeRole.INSTRUCTEUR,
                    administration=request.user.administrations().get(
                        uuid=form.cleaned_data["administration"]
                    ),
                    user=user,
                    group=Group.objects.get(name="instructeur"),
                )
            status = "user_created"
    else:
        form = AddUserForm(
            bailleurs=bailleurs,
            administrations=administrations,
        )
    return {
        "form": form,
        "status": status,
        "editable": True,
    }


def delete_user(request, username):
    User.objects.get(username=username).delete()


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


class ImportBailleurUsersService:
    request: HttpRequest
    upload_form = BailleurListingUploadForm()
    formset = UserBailleurFormSet()
    is_upload: bool = False

    def __init__(self, request: HttpRequest):
        self.request = request

    def get(self) -> ReturnStatus:
        return ReturnStatus.SUCCESS

    def save(self) -> ReturnStatus:
        self.is_upload = self.request.POST.get("Upload", False)
        if self.is_upload:
            return self._process_upload()
        return self._process_formset()

    def _process_upload(self) -> ReturnStatus:
        self.upload_form = BailleurListingUploadForm(
            self.request.POST, self.request.FILES
        )
        if self.upload_form.is_valid():
            data = self.upload_form.cleaned_data["users"]
            self.formset = UserBailleurFormSet(
                self._build_formset_data(data),
                form_kwargs={
                    "bailleur_queryset": Bailleur.objects.filter(
                        id__in=[
                            d["bailleur"].id for d in data if d["bailleur"] is not None
                        ]
                    )
                },
            )
            return ReturnStatus.SUCCESS

        return ReturnStatus.ERROR

    def _process_formset(self) -> ReturnStatus:
        self.formset = UserBailleurFormSet(
            self.request.POST,
            form_kwargs={
                "bailleur_queryset": Bailleur.objects.filter(
                    id__in=[
                        value
                        for key, value in self.request.POST.items()
                        if key.endswith("bailleur")
                    ]
                )
            },
        )
        if self.formset.is_valid():
            for form_user_bailleur in self.formset:
                UserService.create_user_bailleur(
                    form_user_bailleur.cleaned_data["first_name"],
                    form_user_bailleur.cleaned_data["last_name"],
                    form_user_bailleur.cleaned_data["email"],
                    form_user_bailleur.cleaned_data["bailleur"],
                    form_user_bailleur.cleaned_data["username"],
                    self.request.build_absolute_uri("/accounts/login/"),
                )

            messages.success(
                self.request,
                f"{len(self.formset)} utilisateurs bailleurs ont été correctement créés"
                + " à partir du listing",
                extra_tags="Listing importé",
            )
            return ReturnStatus.SUCCESS

        return ReturnStatus.ERROR

    def _build_formset_data(self, results) -> dict:
        data = {
            "form-TOTAL_FORMS": len(results),
            "form-INITIAL_FORMS": len(results),
        }
        for index, user in enumerate(results):
            for key, value in user.items():
                data[f"form-{index}-{key}"] = value
        return data
