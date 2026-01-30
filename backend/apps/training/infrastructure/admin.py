from django.contrib import admin

from apps.training.models import TaskAttempt, Test, TestAttempt, TestItem


class TestItemInline(admin.TabularInline):
    model = TestItem
    extra = 0
    autocomplete_fields = ("task", "exam_task_group")


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "subject", "mode")
    list_filter = ("mode", "subject")
    search_fields = ("title",)
    ordering = ("-id",)
    inlines = (TestItemInline,)


@admin.register(TestItem)
class TestItemAdmin(admin.ModelAdmin):
    list_display = ("id", "test", "order", "task", "max_score", "exam_task_group")
    list_filter = ("test",)
    search_fields = ("test__title",)
    ordering = ("test", "order", "id")
    autocomplete_fields = ("test", "task", "exam_task_group")


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "test", "status", "started_at", "finished_at", "total_score", "max_score")
    list_filter = ("status", "test")
    search_fields = ("user__username", "test__title")
    ordering = ("-id",)
    autocomplete_fields = ("user", "test")


@admin.register(TaskAttempt)
class TaskAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "task", "test_attempt", "score", "is_correct", "submitted_at")
    list_filter = ("is_correct",)
    search_fields = ("user__username", "task__id")
    ordering = ("-id",)
    autocomplete_fields = ("user", "task", "test_attempt")

