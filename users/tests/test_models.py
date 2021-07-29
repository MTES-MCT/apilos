from django.test import TestCase
from users.models import User, Role
from bailleurs.models import Bailleur
from django.contrib.auth.models import Group, Permission
from instructeurs.models import Administration

import datetime

class AdministrationsModelsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_instructeur = User.objects.create(
            username="sabine",
            password="12345",
            first_name="Sabine",
            last_name="Marini",
            email="sabine@appel.com",
        )
        user_bailleur = User.objects.create(
            username="raph",
            password="12345",
            first_name="Raphaëlle",
            last_name="Neyton",
            email="raph@appel.com",
        )
        administration = Administration.objects.create(
            nom="CA d'Arles-Crau-Camargue-Montagnette",
            code="12345",
        )
        bailleur = Bailleur.objects.create(
            nom="3F",
            siret="12345678901234",
            capital_social="SA",
            ville="Marseille",
            dg_nom="Patrick Patoulachi",
            dg_fonction="PDG",
            dg_date_deliberation=datetime.date(2014, 10, 9),
        )
        group_instructeur = Group.objects.create(
            name="Instructeur",
        )
        group_instructeur.permissions.set([
            Permission.objects.get(content_type__model='convention', codename='add_convention'),
            Permission.objects.get(content_type__model='convention', codename='change_convention'),
            Permission.objects.get(content_type__model='convention', codename='delete_convention'),
            Permission.objects.get(content_type__model='convention', codename='view_convention'),
        ])
        group_bailleur = Group.objects.create(
            name="Bailleur",
        )
        group_bailleur.permissions.set([
            Permission.objects.get(content_type__model='convention', codename='add_convention'),
            Permission.objects.get(content_type__model='convention', codename='change_convention'),
            Permission.objects.get(content_type__model='convention', codename='view_convention'),
        ])
        Role.objects.create(
            typologie = Role.TypeRole.BAILLEUR,
            bailleur = bailleur,
            user = user_bailleur,
            group = group_bailleur,
        )
        Role.objects.create(
            typologie = Role.TypeRole.INSTRUCTEUR,
            administration = administration,
            user = user_instructeur,
            group = group_instructeur,
        )
# Test model User
    def test_object_user_str(self):
        user = User.objects.get(username="sabine")
        expected_object_name = f"{user.first_name} {user.last_name}"
        self.assertEqual(str(user), expected_object_name)

    def test_is_role(self):
        user_instructeur = User.objects.get(username="sabine")
        self.assertTrue(user_instructeur.is_instructeur())
        self.assertFalse(user_instructeur.is_bailleur())
        user_bailleur= User.objects.get(username="raph")
        self.assertFalse(user_bailleur.is_instructeur())
        self.assertTrue(user_bailleur.is_bailleur())

    def test_permissions(self):
        user_instructeur = User.objects.get(username="sabine")
        self.assertTrue(user_instructeur.has_perm('convention.change_convention'))
        self.assertTrue(user_instructeur.has_perm('convention.delete_convention'))
        self.assertFalse(user_instructeur.has_perm('bailleur.delete_bailleur'))
        user_bailleur= User.objects.get(username="raph")
        self.assertTrue(user_bailleur.has_perm('convention.change_convention'))
        self.assertFalse(user_bailleur.has_perm('convention.delete_convention'))
        self.assertFalse(user_bailleur.has_perm('bailleur.delete_bailleur'))

    def test_programme_filter(self):
        user_instructeur = User.objects.get(username="sabine")
        self.assertEqual(user_instructeur.programme_filter(), {})
        user_bailleur= User.objects.get(username="raph")
        self.assertEqual(user_bailleur.programme_filter(), {'bailleur_id__in': [user_bailleur.role_set.all()[0].bailleur_id]})

    def test_convention_filter(self):
        user_instructeur = User.objects.get(username="sabine")
        self.assertEqual(user_instructeur.convention_filter(), {'programme__administration_id__in': [user_instructeur.role_set.all()[0].administration_id]})
        user_bailleur= User.objects.get(username="raph")
        self.assertEqual(user_bailleur.convention_filter(), {'bailleur_id__in': [user_bailleur.role_set.all()[0].bailleur_id]})

# Test model Role
    def test_object_role_str(self):
        role = User.objects.get(username="sabine").role_set.all()[0]
        expected_object_name = f"{role.typologie} - {role.administration}"
        self.assertEqual(str(role), expected_object_name)
