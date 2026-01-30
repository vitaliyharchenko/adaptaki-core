from django.urls import path

from .views import TaskTypesView

urlpatterns = [
    path("task-types/", TaskTypesView.as_view()),
]
