from uuid import UUID

from django import forms


class UUIDListForm(forms.Form):
    uuids = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4, "cols": 40}),
        help_text="Enter UUIDs separated by commas or spaces.",
    )

    def clean_uuids(self):
        data = self.cleaned_data["uuids"]
        if not data:
            return []

        uuid_strings = [u.strip() for u in data.replace(",", " ").split()]
        uuids = []
        for u in uuid_strings:
            try:
                uuids.append(UUID(u))
            except ValueError:
                raise forms.ValidationError(f"Invalid UUID: {u}")
        return uuids
