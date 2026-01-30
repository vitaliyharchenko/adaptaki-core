from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import DecimalField, Sum, Value
from django.db.models.functions import Coalesce

from apps.training.application.use_cases import (
    get_random_task_for_session,
    submit_task_answer,
    finish_random_session,
    close_last_random_session,
    RandomTaskNotFound,
    InvalidTestAttempt,
)
from apps.training.models import TestAttempt


class RandomTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Возвращает случайное задание и id текущей рандомной сессии.

        Пример запроса:
            GET /api/training/random-task/?subject_id=1&task_type=short_text

        Пример ответа:
            {
              "id": 123,
              "subject_id": 1,
              "task_type": "short_text",
              "prompt": "...",
              "type_payload": {},
              "test_attempt_id": 555
            }
        """
        subject_id = request.query_params.get("subject_id")
        task_type = request.query_params.get("task_type")
        test_attempt_id = request.query_params.get("test_attempt_id")

        if subject_id is not None:
            try:
                subject_id = int(subject_id)
            except (TypeError, ValueError):
                return Response({"error": "subject_id must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        if test_attempt_id is None:
            close_last_random_session(user=request.user)

        try:
            if test_attempt_id is not None:
                test_attempt_id = int(test_attempt_id)
            task, test_attempt = get_random_task_for_session(
                user=request.user,
                subject_id=subject_id,
                task_type=task_type,
                test_attempt_id=test_attempt_id,
            )
        except RandomTaskNotFound:
            return Response({"error": "No tasks available."}, status=status.HTTP_404_NOT_FOUND)
        except (TypeError, ValueError):
            return Response({"error": "test_attempt_id must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidTestAttempt:
            return Response({"error": "Invalid test_attempt_id."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "id": task.id,
                "subject_id": task.subject_id,
                "task_type": task.task_type,
                "prompt": task.prompt,
                "type_payload": task.type_payload,
                "test_attempt_id": test_attempt.id,
            }
        )


class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Принимает ответ пользователя, проверяет, сохраняет попытку и возвращает результат.

        Пример запроса:
            POST /api/training/submit-answer/
            {
              "task_id": 123,
              "answer_payload": {"value": "масса"},
              "test_attempt_id": 555
            }

        Пример ответа:
            {
              "attempt_id": 999,
              "task_id": 123,
              "is_correct": true,
              "score": "1",
              "max_score": "1",
              "submitted_at": "2026-01-30T12:34:56.789012",
              "solution_text": "..."
            }
        """
        task_id = request.data.get("task_id")
        answer_payload = request.data.get("answer_payload") or {}
        duration_ms = request.data.get("duration_ms")
        test_attempt_id = request.data.get("test_attempt_id")

        if task_id is None:
            return Response({"error": "task_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            task_id = int(task_id)
        except (TypeError, ValueError):
            return Response({"error": "task_id must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        if duration_ms is not None:
            try:
                duration_ms = int(duration_ms)
            except (TypeError, ValueError):
                return Response({"error": "duration_ms must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        if test_attempt_id is not None:
            try:
                test_attempt_id = int(test_attempt_id)
            except (TypeError, ValueError):
                return Response({"error": "test_attempt_id must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            attempt = submit_task_answer(
                user=request.user,
                task_id=task_id,
                answer_payload=answer_payload,
                duration_ms=duration_ms,
                test_attempt_id=test_attempt_id,
            )
        except RandomTaskNotFound:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
        except InvalidTestAttempt:
            return Response({"error": "Invalid test_attempt_id."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "attempt_id": attempt.id,
                "task_id": attempt.task_id,
                "is_correct": attempt.is_correct,
                "score": str(attempt.score),
                "max_score": str(attempt.applied_max_score or 0),
                "submitted_at": attempt.submitted_at.isoformat(),
                "solution_text": attempt.task.solution_text,
                "answer_key": attempt.task.answer_key,
            }
        )


class FinishRandomSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Завершает рандомную сессию (TestAttempt) по запросу клиента.

        Пример запроса:
            POST /api/training/random-session/finish/
            { "test_attempt_id": 555, "status": "finished" }

        Пример ответа:
            { "test_attempt_id": 555, "status": "finished", "finished_at": "..." }
        """
        test_attempt_id = request.data.get("test_attempt_id")
        status_value = request.data.get("status")

        if test_attempt_id is None:
            return Response({"error": "test_attempt_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            test_attempt_id = int(test_attempt_id)
        except (TypeError, ValueError):
            return Response({"error": "test_attempt_id must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            attempt = finish_random_session(
                user=request.user,
                test_attempt_id=test_attempt_id,
                status=status_value,
            )
        except InvalidTestAttempt:
            return Response({"error": "Invalid test_attempt_id."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "test_attempt_id": attempt.id,
                "status": attempt.status,
                "finished_at": attempt.finished_at.isoformat() if attempt.finished_at else None,
            }
        )


class TestAttemptSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Возвращает сводку по попытке теста.

        Пример запроса:
            GET /api/training/test-attempt/summary/?test_attempt_id=555

        Пример ответа:
            {
              "test_attempt_id": 555,
              "status": "finished",
              "started_at": "...",
              "finished_at": "...",
              "total_score": "3",
              "max_score": "5",
              "items": [
                {
                  "attempt_id": 999,
                  "task_id": 123,
                  "task_type": "short_text",
                  "prompt": "...",
                  "answer_payload": {"value": "масса"},
                  "is_correct": true,
                  "score": "1",
                  "max_score": "1",
                  "submitted_at": "...",
                  "solution_text": "..."
                }
              ]
            }
        """
        test_attempt_id = request.query_params.get("test_attempt_id")
        if test_attempt_id is None:
            return Response({"error": "test_attempt_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            test_attempt_id = int(test_attempt_id)
        except (TypeError, ValueError):
            return Response({"error": "test_attempt_id must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        attempt = (
            TestAttempt.objects.select_related("test")
            .filter(id=test_attempt_id, user=request.user)
            .first()
        )
        if attempt is None:
            return Response({"error": "Invalid test_attempt_id."}, status=status.HTTP_400_BAD_REQUEST)

        task_attempts = (
            attempt.task_attempts.select_related("task")
            .order_by("submitted_at")
        )

        totals = task_attempts.aggregate(
            total_score=Coalesce(
                Sum("score"),
                Value(0),
                output_field=DecimalField(max_digits=8, decimal_places=2),
            ),
            max_score=Coalesce(
                Sum(Coalesce("applied_max_score", Value(0))),
                Value(0),
                output_field=DecimalField(max_digits=8, decimal_places=2),
            ),
        )

        return Response(
            {
                "test_attempt_id": attempt.id,
                "status": attempt.status,
                "started_at": attempt.started_at.isoformat(),
                "finished_at": attempt.finished_at.isoformat() if attempt.finished_at else None,
                "total_score": str(totals["total_score"]),
                "max_score": str(totals["max_score"]),
                "items": [
                    {
                        "attempt_id": item.id,
                        "task_id": item.task_id,
                        "task_type": item.task.task_type,
                        "prompt": item.task.prompt,
                        "answer_payload": item.answer_payload,
                        "is_correct": item.is_correct,
                        "score": str(item.score),
                        "max_score": str(item.applied_max_score or 0),
                        "submitted_at": item.submitted_at.isoformat(),
                        "solution_text": item.task.solution_text,
                    }
                    for item in task_attempts
                ],
            }
        )
