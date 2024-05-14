from typing import Any

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.http import HttpRequest
from django.views.decorators.http import require_GET

from bailleurs.models import Bailleur
from instructeurs.models import Administration
from users.models import User


@require_GET
def administration_list(request: HttpRequest) -> dict[str, Any]:
    search_input = request.GET.get("search_input", "")
    order_by = request.GET.get("order_by", "nom")
    page = request.GET.get("page", 1)

    my_administration_list = (
        Administration.objects.all().order_by(order_by)
        if request.user.is_admin
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
    }


@require_GET
def bailleur_list(request: HttpRequest) -> dict[str, Any]:
    bailleur_list_service = BailleurListService(
        search_input=request.GET.get("search_input", ""),
        order_by=request.GET.get("order_by", "nom"),
        page=request.GET.get("page", 1),
        item_list=(
            Bailleur.objects.all().order_by("nom")
            if request.user.is_admin
            else request.user.bailleurs()
        ),
    )
    bailleur_list_service.paginate()
    return bailleur_list_service.as_dict()


@require_GET
def user_list(request: HttpRequest) -> dict[str, Any]:
    user_list_service = UserListService(
        search_input=request.GET.get("search_input", ""),
        order_by=request.GET.get("order_by", "username"),
        page=request.GET.get("page", 1),
        my_user_list=(
            User.objects.exclude(Q(is_staff=True) | Q(is_superuser=True))
            if request.user.is_admin
            else request.user.user_list()
        ),
    )
    user_list_service.paginate()
    return user_list_service.as_dict()


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

    """
    This method should be implemented in the child classes if needed
    """

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
