# apps/learning/api/urls.py

from django.urls import path
from .views import PingView

urlpatterns = [
    path("ping/", PingView.as_view()),
]
