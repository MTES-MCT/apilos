from django.contrib.admin.apps import AdminConfig


class ApilosAdminConfig(AdminConfig):
    default_site = "admin.admin.ApilosAdminSite"
