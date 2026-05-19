from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.create_project),
    path('projects/list/', views.list_projects),
    path('projects/<int:pk>/', views.get_project),
    path('projects/<int:pk>/delete/', views.delete_project),

    path('projects/<int:pk>/places/add/', views.add_place),
    path('places/<int:pk>/', views.update_place),
]