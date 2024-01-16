from typing import Any

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import QuerySet
from django.http import HttpRequest


class IsCloneFilter(SimpleListFilter):
    title = "est un clone"
    parameter_name = "is_clone"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin
    ) -> list[tuple[Any, str]]:
        return (
            ("Oui", "Oui"),
            ("Non", "Non"),
        )

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        match self.value():
            case "Oui":
                return queryset.filter(parent__isnull=False)
            case "Non":
                return queryset.filter(parent__isnull=True)
            case _:
                return queryset
