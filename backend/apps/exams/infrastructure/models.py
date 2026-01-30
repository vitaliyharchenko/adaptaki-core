from django.db import models


class Exam(models.Model):
    title = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Exam"
        verbose_name_plural = "Exams"

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class ExamType(models.Model):
    # Exam + Subject (e.g. EGE Math). "Type" name kept to match current README.
    exam = models.ForeignKey("exams.Exam", on_delete=models.PROTECT, related_name="types")
    subject = models.ForeignKey("graph.Subject", on_delete=models.PROTECT, related_name="exam_types")
    is_active = models.BooleanField(default=True)

    # Optional fields (not required by current README, but useful when you get to versions)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    level = models.CharField(max_length=32, null=True, blank=True)

    class Meta:
        verbose_name = "Exam type"
        verbose_name_plural = "Exam types"
        indexes = [
            models.Index(fields=["exam", "subject", "is_active"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        parts = [self.exam.title, self.subject.title]
        if self.year:
            parts.append(str(self.year))
        if self.level:
            parts.append(self.level)
        return " / ".join(parts)


class ExamTaskGroup(models.Model):
    exam_type = models.ForeignKey(
        "exams.ExamType", on_delete=models.CASCADE, related_name="task_groups"
    )
    num = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    # Exam-mode scoring contract.
    task_type = models.CharField(max_length=64)
    scoring_policy = models.JSONField(default=dict, blank=True)
    max_score = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = "Exam task group"
        verbose_name_plural = "Exam task groups"
        unique_together = [("exam_type", "num")]
        indexes = [
            models.Index(fields=["exam_type", "num"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.exam_type} / {self.num}. {self.title}"


class ExamTaskType(models.Model):
    exam_task_group = models.ForeignKey(
        "exams.ExamTaskGroup", on_delete=models.CASCADE, related_name="task_types"
    )
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Exam task type"
        verbose_name_plural = "Exam task types"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.exam_task_group} / {self.title}"

