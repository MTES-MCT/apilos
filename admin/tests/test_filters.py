from unittest.mock import Mock, patch

from django.db.models import QuerySet
from django.test import TestCase

from admin.filters import IsCloneFilter


class TestIsCloneFilter(TestCase):
    def setUp(self) -> None:
        self.filter = IsCloneFilter(
            request=None, params={}, model=None, model_admin=None
        )

    def test_lookups(self):
        self.assertEqual(
            self.filter.lookups(request=None, model_admin=None),
            (
                ("Oui", "Oui"),
                ("Non", "Non"),
            ),
        )

    def test_queryset_oui(self):
        with patch("admin.filters.IsCloneFilter.value", Mock(return_value="Oui")):
            self.assertEqual(self.filter.value(), "Oui")
            mock_qs = Mock(spec=QuerySet)
            self.filter.queryset(request=None, queryset=mock_qs)
            mock_qs.filter.assert_called_once_with(parent__isnull=False)

    def test_queryset_non(self):
        with patch("admin.filters.IsCloneFilter.value", Mock(return_value="Non")):
            self.assertEqual(self.filter.value(), "Non")
            mock_qs = Mock(spec=QuerySet)
            self.filter.queryset(request=None, queryset=mock_qs)
            mock_qs.filter.assert_called_once_with(parent__isnull=True)

    def test_queryset_none(self):
        self.assertEqual(self.filter.value(), None)
        mock_qs = Mock(spec=QuerySet)
        self.filter.queryset(request=None, queryset=mock_qs)
        mock_qs.filter.assert_not_called()
