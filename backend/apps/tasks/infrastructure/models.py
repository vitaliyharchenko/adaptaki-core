from django.db import models

from apps.tasks.domain.enums import TaskType


class TaskNode(models.Model):
    """
    Связь между заданием (`Task`) и вершиной образовательного графа (`graph.Node`).

    Почему это отдельная модель, а не "просто ManyToMany":
    - это явная таблица связей (проще расширять: вес связи, комментарий методиста, источник и т.п.);
    - можно жестко контролировать уникальность пары (task, node).

    Пример:
        TaskNode.objects.create(task=task, node=node)
    """

    task = models.ForeignKey("tasks.Task", on_delete=models.CASCADE, related_name="task_nodes")
    node = models.ForeignKey("graph.Node", on_delete=models.CASCADE, related_name="node_tasks")

    class Meta:
        verbose_name = "Связь: задание — вершина графа"
        verbose_name_plural = "Связи: задания — вершины графа"
        unique_together = [("task", "node")]
        indexes = [
            models.Index(fields=["task", "node"]),
            models.Index(fields=["node", "task"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.task_id} <-> {self.node_id}"


class Task(models.Model):
    """
    Задание (контент), который можно:
    - показывать в разных клиентах;
    - включать в тесты (`training.TestItem`);
    - решать многократно (это фиксируется в `training.TaskAttempt`).

    Формат контента:
    - `prompt` и `solution_text` храним как Markdown с формулами LaTeX ($...$, $$...$$).

    Расширяемость по типам:
    - `task_type` определяет вид задания;
    - `type_payload` хранит структуру интерфейса (варианты, пары и т.д.);
    - `answer_key` хранит правильный ответ для автопроверки.

    Пример (short_text):
        Task.objects.create(
            subject=math,
            task_type=TaskType.SHORT_TEXT.value,
            prompt="Что такое масса? Ответьте одним словом.",
            type_payload={"max_len": 50},
            answer_key={"correct": ["масса"], "case_sensitive": False},
        )
    """

    subject = models.ForeignKey("graph.Subject", on_delete=models.PROTECT, related_name="tasks")
    task_type = models.CharField(
        max_length=64,
        choices=[(t.value, t.name) for t in TaskType],
    )

    # Content: markdown + LaTeX (rendered on clients).
    prompt = models.TextField()
    solution_text = models.TextField(blank=True, default="")

    # Type-specific structures.
    type_payload = models.JSONField(default=dict, blank=True)
    answer_key = models.JSONField(default=dict, blank=True)

    # Exam rubric (optional).
    exam_task_type = models.ForeignKey(
        "exams.ExamTaskType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )

    # Educational graph mapping.
    nodes = models.ManyToManyField(
        "graph.Node",
        related_name="tasks",
        blank=True,
        through="tasks.TaskNode",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Задание"
        verbose_name_plural = "Задания"
        indexes = [
            models.Index(fields=["subject", "task_type"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.subject.title} / {self.task_type} / {self.id}"
