import pytest

from conventions.tests.factories import ConventionFactory
from programmes.models import Lot, Programme


@pytest.mark.django_db
class TestDeleteConvention:
    def test_delete_convention(self):
        convention = ConventionFactory()
        lot = convention.lot
        programme = lot.programme

        assert lot.conventions.count() == 1
        assert programme.lots.count() == 1

        convention.delete()

        # test lot and programme are deleted
        assert Lot.objects.filter(pk=lot.pk).count() == 0
        assert Programme.objects.filter(pk=programme.pk).count() == 0

    def test_delete_convention_without_deleting_programme(self):
        convention1 = ConventionFactory()
        lot1 = convention1.lot
        programme1 = lot1.programme
        lot2 = Lot.objects.create(programme=programme1)
        ConventionFactory(lot=lot2)

        assert lot1.conventions.count() == 1
        assert programme1.lots.count() == 2

        convention1.delete()

        # test lot and programme are deleted
        assert Lot.objects.filter(pk=lot1.pk).count() == 0
        assert Programme.objects.filter(pk=programme1.pk).count() == 1
