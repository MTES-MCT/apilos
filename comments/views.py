import json

from django.http.response import JsonResponse
from django.views.decorators.http import require_POST

from comments.models import Comment
from conventions.models import Convention


@require_POST
def add_comment(request):
    print(request.POST)
    post_data = json.loads(request.body.decode("utf-8"))
    comment = post_data["comment"].strip()
    convention_uuid = post_data["convention_uuid"]
    convention = Convention.objects.get(uuid=convention_uuid)
    if comment:
        # save comment
        print(post_data)
        Comment.objects.create(
            user=request.user,
            convention=convention,
            message=comment,
            nom_objet=post_data["object"],
            champ_objet=post_data["field"],
        )

        return JsonResponse({"success": "true", "comment": post_data})
    return JsonResponse({"success": "false"})
