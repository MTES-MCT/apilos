from functools import update_wrapper

from django.contrib import admin
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
