from django.db import models


class Exam(models.Model):
    """
    Экзамен (например: ЕГЭ, ОГЭ, ВПР).

    Это верхний уровень рубрикатора.

    Пример:
        Exam.objects.create(title="ЕГЭ")
    """

    title = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Экзамен"
        verbose_name_plural = "Экзамены"

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class ExamType(models.Model):
    """
    Экзамен по предмету (например: ЕГЭ по математике).

    Зачем:
    - один и тот же экзамен может иметь разные структуры заданий по разным предметам;
    - это "контекст", в котором существуют группы/номера заданий (`ExamTaskGroup`).

    Пример:
        ege = Exam.objects.get(title="ЕГЭ")
        math = Subject.objects.get(title="Математика")
        ExamType.objects.create(exam=ege, subject=math, is_active=True)
    """

    # Exam + Subject (e.g. EGE Math). "Type" name kept to match current README.
    exam = models.ForeignKey("exams.Exam", on_delete=models.PROTECT, related_name="types")
    subject = models.ForeignKey("graph.Subject", on_delete=models.PROTECT, related_name="exam_types")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Экзамен по предмету"
        verbose_name_plural = "Экзамены по предметам"
        indexes = [
            models.Index(fields=["exam", "subject", "is_active"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        parts = [self.exam.title, self.subject.title]
        return " / ".join(parts)


class ExamTaskGroup(models.Model):
    """
    Группа/номер экзаменационного задания внутри конкретного `ExamType`.

    Здесь хранится экзаменационная политика оценивания (scoring policy).
    В режиме экзаменационного тренажера проверка ответа может опираться на:
        Task.exam_task_type.exam_task_group.scoring_policy

    Пример:
        group = ExamTaskGroup.objects.create(
            exam_type=exam_type,
            num=13,
            title="Планиметрия",
            scoring_policy={"mode": "binary"},
            max_score=2,
        )
    """

    exam_type = models.ForeignKey(
        "exams.ExamType", on_delete=models.CASCADE, related_name="task_groups"
    )
    num = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    # Exam-mode scoring contract.
    scoring_policy = models.JSONField(default=dict, blank=True)
    max_score = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = "Группа (номер) экзаменационного задания"
        verbose_name_plural = "Группы (номера) экзаменационных заданий"
        unique_together = [("exam_type", "num")]
        indexes = [
            models.Index(fields=["exam_type", "num"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.exam_type} / {self.num}. {self.title}"


class ExamTaskType(models.Model):
    """
    Подтип внутри `ExamTaskGroup` (опциональный уровень детализации).

    Зачем:
    - более точная рубрикация заданий внутри номера/группы;
    - `tasks.Task` может ссылаться на `ExamTaskType` (nullable).

    Пример:
        ExamTaskType.objects.create(
            exam_task_group=group,
            title="Прямоугольный треугольник",
            is_active=True,
        )
    """

    exam_task_group = models.ForeignKey(
        "exams.ExamTaskGroup", on_delete=models.CASCADE, related_name="task_types"
    )
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Тип задания (внутри группы)"
        verbose_name_plural = "Типы заданий (внутри группы)"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.exam_task_group} / {self.title}"
