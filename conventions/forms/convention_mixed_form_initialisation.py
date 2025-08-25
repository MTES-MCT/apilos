import logging
from uuid import UUID

from django import forms

logger = logging.getLogger(__name__)


class UUIDListForm(forms.Form):
    uuids = forms.CharField(required=False)
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
                logger.error(f"Invalid UUID : {u}")
        return uuids

    def clean_action(self):
        action = self.cleaned_data.get("action")
        if action not in ("create", "dispatch"):
            logger.error(f"Invalid action: {action}")
        return action
