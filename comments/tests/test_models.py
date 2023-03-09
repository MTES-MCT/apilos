import uuid

from django.test import TestCase
from conventions.models import Convention
from comments.models import Comment, CommentStatut
from users.models import User


class ConventionModelsTest(TestCase):
    fixtures = [
        "auth.json",
        # "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def test_object_detail(self):
        convention = Convention.objects.get(numero="0001")
        user = User.objects.first()
        comment = Comment.objects.create(
            nom_objet="programme",
            champ_objet="code_postal",
            uuid_objet=uuid.uuid4(),
            convention=convention,
            user=user,
            message="This is a message",
            statut=CommentStatut.OUVERT,
        )
        self.assertEqual(comment.object_detail(), "Code postal de l'opération")
        comment.nom_objet = "logement_edd"
        self.assertEqual(comment.object_detail(), "Tableau de l'EDD simplifié")
        comment.nom_objet = "reference_cadastrale"
        self.assertEqual(comment.object_detail(), "Tableau des références cadastrales")

        comment.nom_objet = "bailleur"
        comment.champ_objet = "code_postal"
        self.assertEqual(comment.object_detail(), "Code postal du bailleur")
        comment.champ_objet = "signataire_nom"
        self.assertEqual(comment.object_detail(), "Nom du signataire du bailleur")
        comment.champ_objet = "unknown_field"
        self.assertEqual(comment.object_detail(), "bailleur - unknown_field")

        comment.nom_objet = "programme"
        comment.champ_objet = "nb_logements"
        self.assertEqual(comment.object_detail(), "Nombre de logements à conventionner")
        comment.champ_objet = "type_operation"
        self.assertEqual(comment.object_detail(), "Type d'opération")
        comment.champ_objet = "unknown_field"
        self.assertEqual(comment.object_detail(), "programme - unknown_field")

        comment.nom_objet = "convention"
        comment.champ_objet = "fond_propre"
        self.assertEqual(comment.object_detail(), "Fonds propres finançant l'opération")
        comment.champ_objet = "commentaires"
        self.assertEqual(
            comment.object_detail(), "Commentaires à l'attention de l'instructeur"
        )
        comment.champ_objet = "unknown_field"
        self.assertEqual(comment.object_detail(), "convention - unknown_field")

        comment.nom_objet = "lot"
        comment.champ_objet = "annexe_caves"
        self.assertEqual(comment.object_detail(), "Option caves dans les annexes")
        comment.champ_objet = "annexe_sechoirs"
        self.assertEqual(comment.object_detail(), "Option séchoirs dans les annexes")
        comment.champ_objet = "unknown_field"
        self.assertEqual(comment.object_detail(), "lot - unknown_field")

        comment.nom_objet = "unknown_object"
        comment.champ_objet = "annexe_caves"
        self.assertEqual(comment.object_detail(), "unknown_object - annexe_caves")
        comment.champ_objet = "unknown_field"
        self.assertEqual(comment.object_detail(), "unknown_object - unknown_field")
