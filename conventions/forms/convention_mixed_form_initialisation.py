from uuid import UUID

from django import forms


class UUIDListForm(forms.Form):
    uuids = forms.CharField(required=False)  # will clean as a list
    action = forms.CharField(required=True)

    def clean_uuids(self):
        data = self.data.getlist("uuids")
        if not data:
            return []

        uuids = []
        for u in data:
            try:
                uuids.append(UUID(u))
            except ValueError:
                raise forms.ValidationError(f"Invalid UUID: {u}")
        return uuids

    def clean_action(self):
        action = self.cleaned_data.get("action")
        if action not in ("create", "dispatch"):
            raise forms.ValidationError(f"Invalid action: {action}")
        return action
