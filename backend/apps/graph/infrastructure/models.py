from django.db import models

from apps.graph.domain.enums import NodeType, RelationType


class Subject(models.Model):
    title = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class Concept(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Concept"
        verbose_name_plural = "Concepts"

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class Node(models.Model):
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
        verbose_name = "Graph node"
        verbose_name_plural = "Graph nodes"
        indexes = [
            models.Index(fields=["subject", "type"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return self.title


class Relation(models.Model):
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
        verbose_name = "Graph relation"
        verbose_name_plural = "Graph relations"
        unique_together = [("parent", "child", "type")]
        indexes = [
            models.Index(fields=["parent", "type"]),
            models.Index(fields=["child", "type"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.parent} -> {self.child} ({self.type})"

