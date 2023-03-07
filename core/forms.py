from typing import Type

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Model


class ModelField(forms.ModelChoiceField):
    """
    Simple form field that convert any given model by its id to an actual instance.
    """

    model: Type[Model]  # The model class to use to perform queries on
    instance: Model | None  # The extracted instance, once data has been cleaned

    def __init__(self, *args, model: Type[Model], **kwargs):
        self.model = model

        super().__init__(queryset=self.model.objects.none(), *args, **kwargs)

    def clean(self, value):
        try:
            self.instance = self.model.objects.get(pk=value)
            return self.instance
        except:
            raise ValidationError(self.error_messages.get("required"), "")
