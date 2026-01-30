from django.conf import settings
from django.db import models

from apps.training.domain.enums import AttemptStatus, TestMode


class Test(models.Model):
    """
    Тест — заранее подготовленная последовательность заданий.

    Важное:
    - сами задания живут в `tasks.Task`;
    - список заданий в тесте хранится в `TestItem` (order + max_score).

    Пример:
        Test.objects.create(
            title="Тренировка: Квадратные уравнения",
            subject=math,
            mode=TestMode.SIMPLE.value,
        )
    """

    title = models.CharField(max_length=255)
    subject = models.ForeignKey("graph.Subject", on_delete=models.PROTECT, related_name="tests")
    mode = models.CharField(
        max_length=32,
        choices=[(m.value, m.name) for m in TestMode],
        default=TestMode.SIMPLE.value,
    )

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"
        indexes = [
            models.Index(fields=["subject", "mode"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class TestItem(models.Model):
    """
    Элемент теста: задание + порядок + максимальный балл в рамках конкретного теста.

    Зачем:
    - переиспользовать один `Task` в нескольких тестах;
    - контролировать порядок выдачи заданий;
    - фиксировать max_score для тестового контекста.

    Пример:
        TestItem.objects.create(test=test, task=task, order=1, max_score=1)
    """

    test = models.ForeignKey("training.Test", on_delete=models.CASCADE, related_name="items")
    task = models.ForeignKey("tasks.Task", on_delete=models.PROTECT, related_name="test_items")
    order = models.PositiveSmallIntegerField()
    max_score = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = "Элемент теста"
        verbose_name_plural = "Элементы теста"
        unique_together = [("test", "order")]
        indexes = [
            models.Index(fields=["test", "order"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.test} / #{self.order}"


class TestAttempt(models.Model):
    """
    Попытка прохождения теста (контейнер).

    Содержит:
    - статус, времена старта/финиша;
    - итоговый балл (снапшот на момент завершения).

    Детализация ответов хранится в `TaskAttempt` (с FK на `test_attempt`).

    Пример:
        attempt = TestAttempt.objects.create(user=user, test=test)
        # ... пользователь решает задания ...
        attempt.status = AttemptStatus.FINISHED.value
        attempt.finished_at = timezone.now()
        attempt.total_score = 7
        attempt.max_score = 10
        attempt.save()
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="test_attempts")
    test = models.ForeignKey("training.Test", on_delete=models.CASCADE, related_name="attempts")

    status = models.CharField(
        max_length=32,
        choices=[(s.value, s.name) for s in AttemptStatus],
        default=AttemptStatus.STARTED.value,
    )

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    # Snapshot totals at finish time (can also be computed from task_attempts).
    total_score = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    max_score = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Попытка теста"
        verbose_name_plural = "Попытки тестов"
        indexes = [
            models.Index(fields=["user", "status", "started_at"]),
            models.Index(fields=["test", "status", "started_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"Attempt {self.id} / {self.user_id} / {self.test_id}"


class TaskAttempt(models.Model):
    """
    Попытка решения задания — атомарный факт "пользователь отправил ответ".

    Почему это важно:
    - это основная сущность для истории обучения и пересчета метрик графа;
    - может существовать как внутри теста (test_attempt != null),
      так и вне тестов (свободная тренировка).

    Поля `applied_scoring_policy` и `applied_max_score` — снапшот,
    чтобы результат был воспроизводим при изменении rubric/правил в будущем.

    Пример (short_text):
        TaskAttempt.objects.create(
            user=user,
            task=task,
            test_attempt=attempt,
            answer_payload={"value": "масса"},
            score=1,
            is_correct=True,
            applied_max_score=1,
            applied_scoring_policy={"mode": "binary"},
        )
    """

    task = models.ForeignKey("tasks.Task", on_delete=models.PROTECT, related_name="attempts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="task_attempts")

    # Nullable to support solving tasks outside tests (practice mode).
    test_attempt = models.ForeignKey(
        "training.TestAttempt",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_attempts",
    )

    answer_payload = models.JSONField(default=dict, blank=True)

    score = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    # Snapshot the applied policy for reproducibility (esp. exam mode).
    applied_scoring_policy = models.JSONField(null=True, blank=True)
    applied_max_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Попытка задания"
        verbose_name_plural = "Попытки заданий"
        indexes = [
            models.Index(fields=["user", "task", "submitted_at"]),
            models.Index(fields=["test_attempt", "submitted_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"TaskAttempt {self.id} / {self.user_id} / {self.task_id}"
