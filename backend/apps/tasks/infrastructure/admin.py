from django.contrib import admin

from apps.tasks.models import Task, TaskNode


class TaskNodeInline(admin.TabularInline):
    model = TaskNode
    extra = 0
    autocomplete_fields = ("node",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "task_type", "exam_task_type", "created_at", "updated_at")
    list_filter = ("subject", "task_type")
    search_fields = ("prompt", "solution_text")
    ordering = ("-id",)
    inlines = (TaskNodeInline,)

    # TaskNode is intentionally not registered as a standalone model in admin.
