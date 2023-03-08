from typing import Type, Callable, Optional

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Model, QuerySet


class ModelField(forms.ModelChoiceField):
    """
    Simple form field that convert any given model by its id to an actual instance.
    """

    field: str
    queryset: QuerySet
    instance: Model | None  # The extracted instance, once data has been cleaned

    def __init__(
        self,
        *args,
        queryset: QuerySet | None = None,
        field: str | None = None,
        **kwargs
    ):
        self.field = field or "id"
        super().__init__(queryset=queryset, *args, **kwargs)

    def _find_instance(self, value):
        self.instance = self.queryset.get(**{self.field: value})
        return self.instance

    def clean(self, value):
        try:
            return self._find_instance(value)
        except:
            raise ValidationError(self.error_messages.get("required"), "")
