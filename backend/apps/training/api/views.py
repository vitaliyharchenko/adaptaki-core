from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from apps.training.application.use_cases import (
    get_random_task_for_session,
    submit_task_answer,
    finish_random_session,
    close_last_random_session,
    RandomTaskNotFound,
    InvalidTestAttempt,
)


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
