from django.urls import path

from .views import RandomTaskView, SubmitAnswerView, FinishRandomSessionView, TestAttemptSummaryView

urlpatterns = [
    path("random-task/", RandomTaskView.as_view()),
    path("submit-answer/", SubmitAnswerView.as_view()),
    path("random-session/finish/", FinishRandomSessionView.as_view()),
    path("test-attempt/summary/", TestAttemptSummaryView.as_view()),
]
