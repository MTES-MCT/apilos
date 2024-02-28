from django.http import HttpRequest

from conventions.forms.convention_form_add import ConventionAddForm


class SelectOperationService:
    request: HttpRequest
    search_filters: dict[str, str] | None

    def __init__(
        self, request: HttpRequest, search_filters: dict[str, str] | None = None
    ) -> None:
        self.request = request
        self.search_filters = search_filters


class ConventionAddService:
    request: HttpRequest
    form: ConventionAddForm

    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        self.form = None

    def get_form(self) -> ConventionAddForm:
        if self.form is None:
            self.form = ConventionAddForm()
        return self.form
