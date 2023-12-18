import json

from django.test import TestCase
from django.urls import reverse

from comments.models import Comment
from conventions.models import Convention


class CommentViewTest(TestCase):
    fixtures = [
        "auth.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def _create_comment(self, convention_uuid):
        return self.client.post(
            reverse("comments:add_comment"),
            data=json.dumps(
                {
                    "comment": "commentaire test",
                    "object_name": "bailleur",
                    "object_field": "nom",
                    "object_uuid": "f910ec86-287c-4420-b032-73f1e40d3a26",
                    "convention_uuid": convention_uuid,
                }
            ),
            content_type="application/json",
        )

    def test_add_comment(self):
        convention = Convention.objects.get(pk=1)
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        response = self._create_comment(str(convention.uuid))

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        comment = Comment.objects.get(uuid=response_json["comment"]["uuid"])
        response_json["comment"].pop("mis_a_jour_le")
        self.assertDictEqual(
            response.json(),
            {
                "success": True,
                "comment": {
                    "uuid": str(comment.uuid),
                    "user_id": 1,
                    "statut": "OUVERT",
                    "username": "nicolas",
                    "is_owner": True,
                    "message": "commentaire test",
                },
                "user": {"is_instructeur": True},
            },
        )

    def test_add_comment_empty(self):
        convention = Convention.objects.get(pk=1)
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})

        response = self.client.post(
            reverse("comments:add_comment"),
            data=json.dumps(
                {
                    "comment": "",
                    "object_name": "bailleur",
                    "object_field": "nom",
                    "object_uuid": "f910ec86-287c-4420-b032-73f1e40d3a26",
                    "convention_uuid": str(convention.uuid),
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {"success": False})

    def test_update_comment(self):
        convention = Convention.objects.get(pk=1)
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})
        response = self._create_comment(convention_uuid=str(convention.uuid))
        comment = Comment.objects.get(uuid=response.json()["comment"]["uuid"])

        response = self.client.post(
            reverse(
                "comments:update_comment", kwargs={"comment_uuid": str(comment.uuid)}
            ),
            data=json.dumps({"message": "commentaire test update", "statut": "RESOLU"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        comment = Comment.objects.get(uuid=response_json["comment"]["uuid"])
        response_json["comment"].pop("mis_a_jour_le")
        self.assertDictEqual(
            response_json,
            {
                "success": True,
                "comment": {
                    "uuid": str(comment.uuid),
                    "user_id": 1,
                    "statut": "RESOLU",
                    "username": "nicolas",
                    "is_owner": True,
                    "message": "commentaire test update",
                },
                "user": {"is_instructeur": True},
            },
        )

    def test_update_comment_empty_message_and_status(self):
        convention = Convention.objects.get(pk=1)
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})
        response = self._create_comment(convention_uuid=str(convention.uuid))
        comment = Comment.objects.get(uuid=response.json()["comment"]["uuid"])

        response = self.client.post(
            reverse(
                "comments:update_comment", kwargs={"comment_uuid": str(comment.uuid)}
            ),
            data=json.dumps({}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.json(),
            {
                "success": False,
            },
        )

    def _get_comment(self, query_params):
        convention = Convention.objects.get(pk=1)
        self.client.post(reverse("login"), {"username": "nicolas", "password": "12345"})
        response = self._create_comment(convention_uuid=str(convention.uuid))
        comment = Comment.objects.get(uuid=response.json()["comment"]["uuid"])
        convention = Convention.objects.get(pk=1)

        get_url = reverse(
            "comments:get_comment", kwargs={"convention_uuid": str(convention.uuid)}
        )
        response = self.client.get(get_url + query_params)

        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        response_json["comments"][0].pop("mis_a_jour_le")
        self.assertDictEqual(
            response_json,
            {
                "comments": [
                    {
                        "is_owner": True,
                        "message": "commentaire test",
                        "statut": "OUVERT",
                        "user_id": 1,
                        "username": "nicolas",
                        "uuid": str(comment.uuid),
                    }
                ],
                "success": True,
                "user": {"is_instructeur": True},
            },
        )

    def test_get_comment_by_object_name(self):
        self._get_comment("?object_name=bailleur")

    def test_get_comment_by_object_field(self):
        self._get_comment("?object_name=bailleur&object_field=nom")

    def test_get_comment_by_object_uuid(self):
        self._get_comment(
            "?object_name=bailleur&object_uuid=f910ec86-287c-4420-b032-73f1e40d3a26"
        )
