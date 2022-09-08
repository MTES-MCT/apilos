from django.contrib import admin

from .models import Convention, Pret


class ConventionAdmin(admin.ModelAdmin):
    list_display = ("view_programme", "uuid")
    search_fields = ["programme__ville", "programme__nom", "uuid"]

    # pylint: disable=R0201
    @admin.display(description="Programme")
    def view_programme(self, obj):
        return (
            f"{obj.programme.ville} -  {obj.programme.nom} - "
            + f"{obj.lot.nb_logements} lgts - "
            + f"{obj.lot.get_type_habitat_display()} - "
            + f"{obj.lot.financement}"
        )


admin.site.register(Convention, ConventionAdmin)
admin.site.register(Pret)
