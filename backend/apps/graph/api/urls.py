from django.urls import path

from .views import SubjectsView

urlpatterns = [
    path("subjects/", SubjectsView.as_view()),
]
