from django.contrib import admin

from apps.graph.models import Concept, Node, Relation, Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title",)
    ordering = ("id",)


@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "subject")
    list_filter = ("subject",)
    search_fields = ("title", "subject__title")
    ordering = ("id",)


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "type", "subject", "concept")
    list_filter = ("type", "subject")
    search_fields = ("title", "subject__title", "concept__title")
    ordering = ("id",)


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ("id", "parent", "child", "type")
    list_filter = ("type",)
    search_fields = ("parent__title", "child__title")
    ordering = ("id",)
