from uuid import uuid4

from django.http import QueryDict
from django.test import TestCase

from conventions.forms.convention_mixed_form_initialisation import UUIDListForm


class UUIDListFormTests(TestCase):
    def test_valid_uuids_and_action_create(self):
        """Should validate correctly with valid UUIDs and 'create' action."""
        qd = QueryDict("", mutable=True)
        qd.setlist("uuids", [str(uuid4()), str(uuid4())])
        qd.update({"action": "create"})

        form = UUIDListForm(qd)
        self.assertTrue(form.is_valid())
        cleaned = form.cleaned_data
        self.assertEqual(cleaned["action"], "create")
        self.assertTrue(all(isinstance(u, type(uuid4())) for u in cleaned["uuids"]))

    def test_valid_action_dispatch(self):
        """Should also accept 'dispatch' as a valid action."""
        qd = QueryDict("", mutable=True)
        qd.setlist("uuids", [str(uuid4())])
        qd.update({"action": "dispatch"})

        form = UUIDListForm(qd)
        self.assertTrue(form.is_valid())

    def test_invalid_action_raises_error(self):
        """Should reject any invalid action value."""
        qd = QueryDict("", mutable=True)
        qd.setlist("uuids", [str(uuid4())])
        qd.update({"action": "delete"})

        form = UUIDListForm(qd)
        self.assertFalse(form.is_valid())
        self.assertIn("Invalid action", form.errors["action"][0])

    def test_invalid_uuid_raises_error(self):
        """Should raise a validation error for invalid UUID strings."""
        qd = QueryDict("", mutable=True)
        qd.setlist("uuids", ["not-a-uuid", str(uuid4())])
        qd.update({"action": "create"})

        form = UUIDListForm(qd)
        self.assertFalse(form.is_valid())
        self.assertIn("Invalid UUIDs", form.errors["uuids"][0])

    def test_empty_uuid_list_returns_empty_list(self):
        """If no uuids are provided, should return an empty list."""
        qd = QueryDict("", mutable=True)
        qd.update({"action": "create"})

        form = UUIDListForm(qd)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["uuids"], [])
