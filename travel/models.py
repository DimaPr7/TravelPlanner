from django.db import models


class TravelProject(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    def update_completion(self):
        places = self.places.all()
        if places.exists() and all(p.visited for p in places):
            self.completed = True
            self.save()


class ProjectPlace(models.Model):
    project = models.ForeignKey(
        TravelProject,
        on_delete=models.CASCADE,
        related_name = 'places'
    )
    external_id = models.IntegerField()
    title = models.CharField(max_length=200)
    notes = models.TextField(null=True, blank=True)
    visited = models.BooleanField(default=False)

