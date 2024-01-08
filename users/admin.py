from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from admin.admin import ApilosModelAdmin
from bailleurs.models import Bailleur
from instructeurs.models import Administration

from .models import Role, User


@admin.register(Role)
class CustomAdministrationAdmin(ApilosModelAdmin):
    list_select_related = ("administration", "bailleur", "user")
    readonly_fields = ("administration", "bailleur", "user")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "administration":
            kwargs["queryset"] = Administration.objects.order_by("nom")
        if db_field.name == "bailleur":
            kwargs["queryset"] = Bailleur.objects.order_by("nom")
        if db_field.name in "user":
            kwargs["queryset"] = User.objects.order_by("first_name", "last_name")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ApilosModelAdmin):
    pass
