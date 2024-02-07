from django.contrib import admin
from waffle.admin import FlagAdmin, SampleAdmin, SwitchAdmin
from waffle.models import Flag, Sample, Switch

from admin.admin import ApilosModelAdmin


class WaffleCustomAdminMixin(ApilosModelAdmin):
    staff_user_can_view = True
    staff_user_can_change = True
    staff_user_can_add = True
    staff_user_can_delete = True


class FlagUserInline(admin.TabularInline):
    model = Flag.users.through
    extra = 1
    verbose_name_plural = "Activer ce flag pour ces utilisateurs"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = self.get_field_queryset(
                kwargs.get("using"), db_field, request
            ).order_by("last_name")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Flag)
class CustomFlagAdmin(WaffleCustomAdminMixin, FlagAdmin):
    inlines = (FlagUserInline,)
    fields = (
        "name",
        "everyone",
        "superusers",
        "staff",
        "authenticated",
        "groups",
        "note",
        "users",
    )
    readonly_fields = ("name",)


@admin.register(Sample)
class CustomSampleAdmin(WaffleCustomAdminMixin, SampleAdmin):
    pass


@admin.register(Switch)
class CustomSwitchAdmin(WaffleCustomAdminMixin, SwitchAdmin):
    pass
