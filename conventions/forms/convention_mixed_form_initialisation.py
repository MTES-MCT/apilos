from uuid import UUID

from django import forms


class UUIDListForm(forms.Form):
    uuids = forms.CharField(required=False)
    action = forms.CharField(required=True)

    def clean_uuids(self):
        raw_uuids = self.data.getlist("uuids")
        if not raw_uuids:
            return []

        uuids = []
        errors = []
        for u in raw_uuids:
            try:
                uuids.append(UUID(u))
            except ValueError:
                errors.append(u)

        if errors:
            raise forms.ValidationError(f"Invalid UUIDs: {', '.join(errors)}")

        return uuids

    def clean_action(self):
        action = self.cleaned_data.get("action")
        if action not in ("create", "dispatch"):
            raise forms.ValidationError(f"Invalid action: {action}")
        return action
