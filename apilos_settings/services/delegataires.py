import json

from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db import models
from django.db.models import F, Q, QuerySet
from django.http import HttpRequest

from apilos_settings.forms.delegataires_form import DelegatairesForm
from conventions.forms.upload import UploadForm
from conventions.models.convention import Convention
from conventions.services.selection import _get_choices_from_object
from conventions.templatetags.custom_filters import is_instructeur
from instructeurs.models import Administration
from programmes.models.models import Programme


class DelegatairesService:
    request: HttpRequest
    form: DelegatairesForm
    upform: UploadForm

    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    def create_forms(self):
        admins = self._get_administration_choices()
        if self.request.POST:
            self.form = DelegatairesForm(self.request.POST, administrations=admins)
            self.upform = UploadForm(self.request.POST, self.request.FILES)
        else:
            self.form = DelegatairesForm(administrations=admins)
            self.upform = UploadForm()

    def _get_administration_choices(self):
        return _get_choices_from_object(
            self.request.user.administrations()
            if is_instructeur(self.request)
            else Administration.objects.all().order_by("nom")
        )

    def get_success_message(self, conventions_count, new_admin):
        return f"Succès de la réassignation de {conventions_count} conventions à l'administration {new_admin}."

    def get_reassignation_data(self):
        new_admin = Administration.objects.get(uuid=self.form.data["administration"])
        code_insee_departement = self.form.data["departement"]
        communes = self.form.data.get("communes")
        if communes:
            communes = json.loads(communes)

        if communes:
            programmes = self._get_programme_qs_from_communes(communes)
        else:
            programmes = self._get_programme_qs_from_dpts(code_insee_departement)
        programmes.exclude(administration=new_admin).select_related("administration")

        conventions = Convention.objects.filter(programme__in=programmes)

        old_admins = (
            programmes.values("administration__code")
            .distinct()
            .annotate(count=models.Count("pk"))
        )

        return {
            "programmes_count": programmes.count(),
            "conventions_count": conventions.count(),
            "old_admins": old_admins,
            "new_admin": new_admin,
            "conventions": conventions[:10],
            "programmes": programmes,
        }

    def reassign(self, programmes, new_admin):
        programmes.update(reassign_command_old_admin_backup=F("administration_id"))
        programmes.update(administration=new_admin)
        self.success = True

    def _get_programme_qs_from_dpts(self, departement) -> QuerySet[Programme]:
        return Programme.objects.filter(code_insee_departement=departement)

    def _get_programme_qs_from_communes(self, communes) -> QuerySet[Programme]:
        queryset = Programme.objects.annotate(
            search_vector_ville=SearchVector("ville", config="french")
        )

        filters = Q()
        for item in communes:
            filters |= Q(
                code_postal=item["code_postal"],
                search_vector_ville=SearchQuery(item["commune"], config="french"),
            )

        return queryset.filter(filters)
