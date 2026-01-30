from django.conf import settings
from django.db import models

from apps.training.domain.enums import AttemptStatus, TestMode


class Test(models.Model):
    title = models.CharField(max_length=255)
    subject = models.ForeignKey("graph.Subject", on_delete=models.PROTECT, related_name="tests")
    mode = models.CharField(
        max_length=32,
        choices=[(m.value, m.name) for m in TestMode],
        default=TestMode.SIMPLE.value,
    )

    class Meta:
        verbose_name = "Test"
        verbose_name_plural = "Tests"
        indexes = [
            models.Index(fields=["subject", "mode"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class TestItem(models.Model):
    test = models.ForeignKey("training.Test", on_delete=models.CASCADE, related_name="items")
    task = models.ForeignKey("tasks.Task", on_delete=models.PROTECT, related_name="test_items")
    order = models.PositiveSmallIntegerField()
    max_score = models.PositiveSmallIntegerField(default=1)

    # In exam mode this can point to the rubric group to apply scoring policy.
    exam_task_group = models.ForeignKey(
        "exams.ExamTaskGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="test_items",
    )

    class Meta:
        verbose_name = "Test item"
        verbose_name_plural = "Test items"
        unique_together = [("test", "order")]
        indexes = [
            models.Index(fields=["test", "order"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.test} / #{self.order}"


class TestAttempt(models.Model):
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
        verbose_name = "Test attempt"
        verbose_name_plural = "Test attempts"
        indexes = [
            models.Index(fields=["user", "status", "started_at"]),
            models.Index(fields=["test", "status", "started_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"Attempt {self.id} / {self.user_id} / {self.test_id}"


class TaskAttempt(models.Model):
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
        verbose_name = "Task attempt"
        verbose_name_plural = "Task attempts"
        indexes = [
            models.Index(fields=["user", "task", "submitted_at"]),
            models.Index(fields=["test_attempt", "submitted_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"TaskAttempt {self.id} / {self.user_id} / {self.task_id}"

