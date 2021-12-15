from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from programmes.models import Programme
from programmes.api.serializers import ProgrammeSerializer


@csrf_exempt
def programme_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    print("list")
    if request.method == "GET":
        snippets = Programme.objects.all()
        serializer = ProgrammeSerializer(snippets, many=True)
        return JsonResponse(serializer.data, safe=False)

    if request.method == "POST":
        data = JSONParser().parse(request)
        serializer = ProgrammeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    return JsonResponse({"error": "route error"}, status=400)


@csrf_exempt
def programme_detail(request, uuid):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        programme = Programme.objects.get(uuid=uuid)
    except Programme.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = ProgrammeSerializer(programme)
        return JsonResponse(serializer.data)

    if request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = ProgrammeSerializer(programme, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    if request.method == "DELETE":
        programme.delete()
        return HttpResponse(status=204)

    return JsonResponse({"error": "route error"}, status=400)
