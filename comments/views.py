import json

from django.http.response import JsonResponse
from django.views.decorators.http import require_POST

from comments.models import Comment
from conventions.models import Convention


@require_POST
def add_comment(request):
    post_data = json.loads(request.body.decode("utf-8"))
    comment = post_data["comment"].strip()
    convention_uuid = post_data["convention_uuid"]
    convention = Convention.objects.get(uuid=convention_uuid)
    if comment:
        # save comment
        comment = Comment.objects.create(
            user=request.user,
            convention=convention,
            message=comment,
            nom_objet=post_data["object_name"],
            champ_objet=post_data["object_field"],
            uuid_objet=post_data["object_uuid"],
        )

        return JsonResponse(
            {
                "success": True,
                "comment": {
                    "uuid": comment.uuid,
                    "user_id": comment.user_id,
                    "statut": comment.statut,
                    "username": str(comment.user),
                    "is_owner": bool(comment.user_id == request.user.id),
                    "mis_a_jour_le": comment.mis_a_jour_le.strftime(
                        "%e %B %Y %H:%M"
                    ).lower(),
                    "message": comment.message,
                },
                "user": {"is_instructeur": request.user.is_instructeur()},
            }
        )
    return JsonResponse({"success": False})


@require_POST
def update_comment(request, comment_uuid):
    post_data = json.loads(request.body.decode("utf-8"))
    message = post_data["message"].strip() if "message" in post_data else None
    statut = post_data["statut"] if "statut" in post_data else None
    if message is not None or statut is not None:
        comment = Comment.objects.get(uuid=comment_uuid)
        if message:
            comment.message = message
        if statut:
            comment.statut = statut
        comment.save()
        return JsonResponse(
            {
                "success": True,
                "comment": {
                    "uuid": comment.uuid,
                    "user_id": comment.user_id,
                    "statut": comment.statut,
                    "username": str(comment.user),
                    "is_owner": bool(comment.user_id == request.user.id),
                    "mis_a_jour_le": comment.mis_a_jour_le.strftime(
                        "%e %B %Y %H:%M"
                    ).lower(),
                    "message": comment.message,
                },
                "user": {"is_instructeur": request.user.is_instructeur()},
            }
        )
    return JsonResponse({"success": False})
