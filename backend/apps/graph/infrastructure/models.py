from django.db import models

from apps.graph.domain.enums import NodeType, RelationType


class Subject(models.Model):
    """
    Предмет (например: Математика, Физика).

    Используется как общий справочник для:
    - рубрикатора экзаменов (`exams.ExamType.subject`);
    - банка заданий (`tasks.Task.subject`);
    - тестов (`training.Test.subject`);
    - графа (`Node.subject`, `Concept.subject`).

    Пример:
        Subject.objects.create(title="Математика")
    """

    title = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class Concept(models.Model):
    """
    Концепция/тема внутри предмета (например: "Квадратные уравнения").

    Зачем:
    - группировать вершины графа и задания на уровне тем;
    - использовать для навигации и фильтрации.

    Пример:
        math = Subject.objects.get(title="Математика")
        Concept.objects.create(title="Квадратные уравнения", subject=math)
    """

    title = models.CharField(max_length=255)
    subject = models.ForeignKey(
        "graph.Subject",
        on_delete=models.PROTECT,
        related_name="concepts",
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Концепция"
        verbose_name_plural = "Концепции"

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class Node(models.Model):
    """
    Вершина образовательного графа: знание/навык/понятие.

    Зачем:
    - на вершины будут "вешаться" метрики ученика;
    - задания (`tasks.Task`) связываются с вершинами через `tasks.TaskNode`,
      чтобы результаты решения влияли на навыки/знания.

    Пример:
        math = Subject.objects.get(title="Математика")
        concept = Concept.objects.get(title="Квадратные уравнения")
        Node.objects.create(
            title="Теорема Виета",
            type=NodeType.CONCEPT.value,
            subject=math,
            concept=concept,
        )
    """

    title = models.CharField(max_length=255)
    type = models.CharField(
        max_length=32,
        choices=[(t.value, t.name) for t in NodeType],
        default=NodeType.CONCEPT.value,
    )
    subject = models.ForeignKey("graph.Subject", on_delete=models.PROTECT, related_name="nodes")
    concept = models.ForeignKey(
        "graph.Concept", on_delete=models.SET_NULL, related_name="nodes", null=True, blank=True
    )

    class Meta:
        verbose_name = "Вершина графа"
        verbose_name_plural = "Вершины графа"
        indexes = [
            models.Index(fields=["subject", "type"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class Relation(models.Model):
    """
    Ребро графа: связь между двумя вершинами.

    Зачем:
    - описывать зависимости (пререквизиты), вложенность и другие отношения.

    Пример:
        Relation.objects.create(
            parent=node_a,
            child=node_b,
            type=RelationType.PREREQUISITE.value,
        )
    """

    parent = models.ForeignKey(
        "graph.Node", on_delete=models.CASCADE, related_name="relations_out"
    )
    child = models.ForeignKey(
        "graph.Node", on_delete=models.CASCADE, related_name="relations_in"
    )
    type = models.CharField(
        max_length=32,
        choices=[(t.value, t.name) for t in RelationType],
        default=RelationType.PREREQUISITE.value,
    )

    class Meta:
        verbose_name = "Связь графа"
        verbose_name_plural = "Связи графа"
        unique_together = [("parent", "child", "type")]
        indexes = [
            models.Index(fields=["parent", "type"]),
            models.Index(fields=["child", "type"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.parent} -> {self.child} ({self.type})"
