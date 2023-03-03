from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from bailleurs.models import Bailleur
from instructeurs.models import Administration
from users.models import User
from .models import User, Role


class CustomAdministrationAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "administration":
            kwargs["queryset"] = Administration.objects.order_by("nom")
        if db_field.name == "bailleur":
            kwargs["queryset"] = Bailleur.objects.order_by("nom")
        if db_field.name in "user":
            kwargs["queryset"] = User.objects.order_by("first_name", "last_name")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CustomUserAdmin(UserAdmin):
    UserAdmin.fieldsets += (
        ("Informations supplémentaires", {"fields": ("read_popup",)}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Role, CustomAdministrationAdmin)
