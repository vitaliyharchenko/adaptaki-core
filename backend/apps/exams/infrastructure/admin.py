from django.contrib import admin

from apps.exams.models import Exam, ExamTaskGroup, ExamTaskType, ExamType


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title",)
    ordering = ("id",)


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "exam", "subject", "year", "level", "is_active")
    list_filter = ("is_active", "exam", "subject", "year", "level")
    search_fields = ("exam__title", "subject__title")
    ordering = ("id",)


@admin.register(ExamTaskGroup)
class ExamTaskGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "exam_type", "num", "title", "task_type", "max_score", "is_active")
    list_filter = ("is_active", "exam_type", "task_type")
    search_fields = ("title", "exam_type__exam__title", "exam_type__subject__title")
    ordering = ("exam_type", "num", "id")


@admin.register(ExamTaskType)
class ExamTaskTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "exam_task_group", "title", "is_active")
    list_filter = ("is_active", "exam_task_group")
    search_fields = ("title", "exam_task_group__title")
    ordering = ("id",)

