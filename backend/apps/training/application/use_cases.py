from __future__ import annotations

from django.db.models import QuerySet
from django.utils import timezone

from apps.graph.models import Subject
from apps.tasks.models import Task
from apps.training.models import TaskAttempt, TestAttempt
from apps.tasks.application.answer_check import check_task_answer
from apps.training.domain.enums import AttemptStatus, TestMode


class RandomTaskNotFound(Exception):
    pass


class InvalidTestAttempt(Exception):
    pass


def get_random_task_for_user(*, user, subject_id: int | None = None, task_type: str | None = None) -> Task:
    """
    Выбирает случайное задание по фильтрам (предмет, тип).

    Пример:
        task = get_random_task_for_user(user=request.user, subject_id=1, task_type="short_text")
    """
    tasks = Task.objects.all()
    tasks = _apply_task_filters(tasks, subject_id=subject_id, task_type=task_type)
    task = tasks.order_by("?").first()
    if task is None:
        raise RandomTaskNotFound("No tasks available for the given filters.")
    return task


def get_random_task_for_session(
    *,
    user,
    subject_id: int | None = None,
    task_type: str | None = None,
    test_attempt_id: int | None = None,
) -> tuple[Task, TestAttempt]:
    """
    Возвращает случайное задание и активную сессию (TestAttempt) для рандомного режима.

    Логика:
    - если передан test_attempt_id, проверяет владение и статус started;
    - если нет, создаёт новую сессию на основе предмета выбранного задания.

    Пример:
        task, session = get_random_task_for_session(user=request.user, subject_id=1)
    """
    test_attempt = None
    if test_attempt_id is not None:
        test_attempt = (
            TestAttempt.objects.select_related("test__subject")
            .filter(id=test_attempt_id, user=user, status=AttemptStatus.STARTED.value)
            .first()
        )
        if test_attempt is None:
            raise InvalidTestAttempt("Test attempt does not belong to user or is not started.")
        if subject_id is not None and subject_id != test_attempt.test.subject_id:
            raise InvalidTestAttempt("Test attempt subject mismatch.")
        subject_id = test_attempt.test.subject_id

    tasks = Task.objects.all()
    tasks = _apply_task_filters(tasks, subject_id=subject_id, task_type=task_type)
    task = tasks.order_by("?").first()
    if task is None:
        raise RandomTaskNotFound("No tasks available for the given filters.")

    if test_attempt is None:
        test_attempt = _create_random_test_attempt(user=user, subject=task.subject)

    return task, test_attempt


def submit_task_answer(
    *,
    user,
    task_id: int,
    answer_payload: dict | None,
    duration_ms: int | None = None,
    test_attempt_id: int | None = None,
) -> TaskAttempt:
    """
    Принимает ответ пользователя, проверяет его и сохраняет TaskAttempt.

    Пример:
        attempt = submit_task_answer(
            user=request.user,
            task_id=123,
            answer_payload={"value": "масса"},
            duration_ms=4200,
        )
    """
    task = Task.objects.select_related("subject").filter(id=task_id).first()
    if task is None:
        raise RandomTaskNotFound("Task not found.")

    test_attempt = None
    if test_attempt_id is not None:
        test_attempt = TestAttempt.objects.filter(id=test_attempt_id, user=user).first()
        if test_attempt is None:
            raise InvalidTestAttempt("Test attempt does not belong to user.")

    if answer_payload is None:
        answer_payload = {}
    if not isinstance(answer_payload, dict):
        answer_payload = {"value": answer_payload}

    check_result = check_task_answer(task, answer_payload)

    attempt = TaskAttempt.objects.create(
        user=user,
        task=task,
        test_attempt=test_attempt,
        answer_payload=answer_payload or {},
        score=check_result.score,
        is_correct=check_result.is_correct,
        duration_ms=duration_ms,
        applied_scoring_policy=check_result.applied_scoring_policy,
        applied_max_score=check_result.max_score,
    )

    return attempt


def _apply_task_filters(
    tasks: QuerySet[Task],
    *,
    subject_id: int | None,
    task_type: str | None,
) -> QuerySet[Task]:
    """
    Применяет фильтры к QuerySet заданий.

    Пример:
        tasks = _apply_task_filters(Task.objects.all(), subject_id=1, task_type="number")
    """
    if subject_id is not None:
        tasks = tasks.filter(subject_id=subject_id)
    if task_type:
        tasks = tasks.filter(task_type=task_type)
    return tasks


def _create_random_test_attempt(*, user, subject: Subject) -> TestAttempt:
    """
    Создает TestAttempt для рандомной практики по конкретному предмету.

    Пример:
        attempt = _create_random_test_attempt(user=request.user, subject=math_subject)
    """
    test = _get_or_create_random_test(subject)
    return TestAttempt.objects.create(user=user, test=test)


def _get_or_create_random_test(subject: Subject):
    """
    Получает или создает служебный тест "Random practice — <Subject>".

    Пример:
        test = _get_or_create_random_test(subject=math_subject)
    """
    title = f"Random practice — {subject.title}"
    test, _ = subject.tests.get_or_create(
        title=title,
        mode=TestMode.SIMPLE.value,
    )
    return test


def finish_random_session(*, user, test_attempt_id: int, status: str | None = None) -> TestAttempt:
    """
    Завершает рандомную сессию, выставляя статус и время окончания.

    Пример:
        finish_random_session(user=request.user, test_attempt_id=555, status="finished")
    """
    attempt = TestAttempt.objects.filter(id=test_attempt_id, user=user).first()
    if attempt is None:
        raise InvalidTestAttempt("Test attempt does not belong to user.")

    if attempt.status != AttemptStatus.STARTED.value:
        return attempt

    if status is not None and status not in {s.value for s in AttemptStatus}:
        raise InvalidTestAttempt("Invalid status.")

    attempt.status = status or AttemptStatus.FINISHED.value
    attempt.finished_at = timezone.now()
    attempt.save(update_fields=["status", "finished_at"])
    return attempt


def close_last_random_session(*, user) -> TestAttempt | None:
    """
    Закрывает последнюю незавершенную рандомную сессию пользователя (если есть).

    Пример:
        close_last_random_session(user=request.user)
    """
    attempt = (
        TestAttempt.objects.select_related("test")
        .filter(
            user=user,
            status=AttemptStatus.STARTED.value,
            test__title__startswith="Random practice — ",
        )
        .order_by("-started_at")
        .first()
    )
    if attempt is None:
        return None

    attempt.status = AttemptStatus.ABANDONED.value
    attempt.finished_at = timezone.now()
    attempt.save(update_fields=["status", "finished_at"])
    return attempt
