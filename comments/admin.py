from django.contrib import admin

from admin.admin import ApilosModelAdmin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(ApilosModelAdmin):
    readonly_fields = (
        "convention",
        "nom_objet",
        "champ_objet",
        "uuid_objet",
    )
    list_display = (
        "id",
        "convention",
        "linked_object",
        "statut",
    )
    list_filter = ("statut",)

    @admin.display(description="Objet lié")
    def linked_object(self, obj: Comment) -> str:
        return "".join(
            [
                obj.nom_objet,
                f" (#{obj.uuid_objet})" if obj.uuid_objet else "",
                (
                    f" - {obj.champ_objet}"
                    if obj.champ_objet and obj.champ_objet != "all"
                    else ""
                ),
            ]
        )
