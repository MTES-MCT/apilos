from django.contrib import admin
from waffle.admin import FlagAdmin, SampleAdmin, SwitchAdmin
from waffle.models import Flag, Sample, Switch

from admin.admin import ApilosModelAdmin


class WaffleCustomAdminMixin(ApilosModelAdmin):
    staff_user_can_view = True
    staff_user_can_change = True
    staff_user_can_add = True
    staff_user_can_delete = True


@admin.register(Flag)
class CustomFlagAdmin(WaffleCustomAdminMixin, FlagAdmin):
    pass


@admin.register(Sample)
class CustomSampleAdmin(WaffleCustomAdminMixin, SampleAdmin):
    pass


@admin.register(Switch)
class CustomSwitchAdmin(WaffleCustomAdminMixin, SwitchAdmin):
    pass
