from functools import update_wrapper
from typing import Any

from django.contrib import admin
from django.http.request import HttpRequest
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect


class ApilosAdminSite(admin.AdminSite):
    def login(self, request, extra_context=None):
        """
        Disable login page
        """
        return render(request, "404.html", status=404)

    def admin_view(self, view, cacheable=False):
        """
        If user staff is logged, browse admin as usual. Otherwise display 404 page
        like admin is not installed.
        """

        def inner(request, *args, **kwargs):
            if not self.has_permission(request):
                return render(request, "404.html", status=404)
            return view(request, *args, **kwargs)

        if not cacheable:
            inner = never_cache(inner)
        # We add csrf_protect here so this function can be used as a utility
        # function for any view, without having to repeat 'csrf_protect'.
        if not getattr(view, "csrf_exempt", False):
            inner = csrf_protect(inner)
        return update_wrapper(inner, view)


class ApilosModelAdmin(admin.ModelAdmin):
    staff_user_can_view: bool = True
    staff_user_can_change: bool = True
    staff_user_can_add: bool = True
    staff_user_can_delete: bool = False

    def has_module_permission(self, request: HttpRequest) -> bool:
        if request.user.is_staff:
            return True
        return super().has_module_permission(request)

    def has_view_permission(self, request: HttpRequest, obj: Any | None = None) -> bool:
        if request.user.is_staff and self.staff_user_can_view:
            return True
        return super().has_view_permission(request, obj)

    def has_change_permission(
        self, request: HttpRequest, obj: Any | None = None
    ) -> bool:
        if request.user.is_staff and self.staff_user_can_change:
            return True
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request: HttpRequest) -> bool:
        if request.user.is_staff and self.staff_user_can_add:
            return True
        return super().has_add_permission(request)

    def has_delete_permission(
        self, request: HttpRequest, obj: Any | None = None
    ) -> bool:
        if request.user.is_staff and self.staff_user_can_delete:
            return True
        return super().has_delete_permission(request, obj)
