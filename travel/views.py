import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TravelProject, ProjectPlace
from .services import fetch_artwork


@csrf_exempt
def create_project(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body)

    project = TravelProject.objects.create(
        title=data["title"],
        description=data.get("description"),
        start_date=data.get("start_date")
    )

    places = data.get("places", [])

    if len(places) > 10:
        return JsonResponse({"error": "Max 10 places"}, status=400)

    for p in places:
        external_id = p["external_id"]

        if ProjectPlace.objects.filter(
            project=project,
            external_id=external_id
        ).exists():
            return JsonResponse({"error": "Duplicate place"}, status=400)

        art = fetch_artwork(external_id)
        if not art:
            return JsonResponse({"error": "Invalid external_id"}, status=404)

        ProjectPlace.objects.create(
            project=project,
            external_id=external_id,
            title=art.get("title", "Unknown")
        )

    return JsonResponse({"id": project.id})

def list_projects(request):
    projects = TravelProject.objects.all()

    return JsonResponse([
        {
            "id": p.id,
            "title": p.title,
            "completed": p.completed
        }
        for p in projects
    ], safe=False)


def get_project(request, pk):
    try:
        p = TravelProject.objects.get(id=pk)
    except TravelProject.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    return JsonResponse({
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "start_date": p.start_date,
        "completed": p.completed,
        "places": [
            {
                "id": pl.id,
                "external_id": pl.external_id,
                "title": pl.title,
                "notes": pl.notes,
                "visited": pl.visited
            }
            for pl in p.places.all()
        ]
    })


@csrf_exempt
def delete_project(request, pk):
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE only"}, status=405)

    try:
        project = TravelProject.objects.get(id=pk)
    except TravelProject.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    if project.places.filter(visited=True).exists():
        return JsonResponse(
            {"error": "Cannot delete project with visited places"},
            status=400
        )

    project.delete()
    return JsonResponse({"status": "deleted"})


@csrf_exempt
def add_place(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body)
    external_id = data["external_id"]

    project = TravelProject.objects.get(id=pk)

    if project.places.count() >= 10:
        return JsonResponse({"error": "Max 10 places"}, status=400)

    if ProjectPlace.objects.filter(
        project=project,
        external_id=external_id
    ).exists():
        return JsonResponse({"error": "Duplicate place"}, status=400)

    art = fetch_artwork(external_id)
    if not art:
        return JsonResponse({"error": "Invalid place"}, status=404)

    place = ProjectPlace.objects.create(
        project=project,
        external_id=external_id,
        title=art.get("title", "Unknown")
    )

    return JsonResponse({"id": place.id})


@csrf_exempt
def update_place(request, pk):
    if request.method != "PATCH":
        return JsonResponse({"error": "PATCH only"}, status=405)

    data = json.loads(request.body)

    try:
        place = ProjectPlace.objects.get(id=pk)
    except ProjectPlace.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    if "notes" in data:
        place.notes = data["notes"]

    if "visited" in data:
        place.visited = data["visited"]

    place.save()

    place.project.update_completion()

    return JsonResponse({"status": "updated"})