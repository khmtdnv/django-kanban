from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter
from django.db.models import Avg, Count, Q

from .models.project import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Метрики
    1) Среднее время выполнения задачи
    2) Количество блокирующих задач
    3) Прогнозирования сроков выполнения проекта на основе исторических данных
    (то есть количество оставшихся задача * среднее время выполнения)
    """

    list_display = (
        "name",
        "owner",
        "created_at",
        "updated_at",
        "total_tasks",
        "completed_tasks",
        "average_task_complete_time",
        "blocking_tasks",
        "project_progress",
        "project_completion_forecast",
    )
    fields = ("members",)
    autocomplete_fields = ("members",)
    search_fields = (
        "name",
        "owner__phone_number",
    )
    list_filter = (
        ("owner", RelatedOnlyFieldListFilter),
        "created_at",
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _total_tasks=Count("tasks", distinct=True),
            _avg_time=Avg(
                "tasks__actual_time",
                filter=Q(tasks__column__name="Завершено"),
            ),
            _blocking_tasks=Count(
                "tasks",
                filter=Q(tasks__priority="CRITICAL"),
                distinct=True,
            ),
            _completed_tasks=Count(
                "tasks",
                filter=Q(tasks__column__name="Завершено"),
                distinct=True,
            ),
        )
        return queryset

    @admin.display(description="Всего задач", ordering="_total_tasks")
    def total_tasks(self, obj):
        return obj._total_tasks

    @admin.display(description="Завершено задач", ordering="_completed_tasks")
    def completed_tasks(self, obj):
        return obj._completed_tasks

    @admin.display(description="Среднее время выполнения задачи", ordering="_avg_time")
    def average_task_complete_time(self, obj):
        if not obj._avg_time:
            return "-"

        total_seconds = int(obj._avg_time.total_seconds())
        minutes = (total_seconds % 3600) // 60
        hours = (total_seconds % 86400) // 3600
        days = total_seconds // 86400

        parts = []
        if days > 0:
            parts.append(f"{days}д")
        if hours > 0:
            parts.append(f"{hours}ч")
        if minutes > 0:
            parts.append(f"{minutes}м")

        return " ".join(parts)

    @admin.display(description="Блокирующих задач", ordering="_blocking_tasks")
    def blocking_tasks(self, obj):
        return obj._blocking_tasks

    @admin.display(description="Прогресс проекта")
    def project_progress(self, obj):
        if obj._total_tasks == 0:
            return "0%"

        if obj._completed_tasks == 0:
            return "0%"

        percent = (obj._completed_tasks / obj._total_tasks) * 100

        return f"{int(percent)}%"

    @admin.display(description="Прогноз сроков выполнения проекта")
    def project_completion_forecast(self, obj):
        if not obj._avg_time:
            return "-"

        tasks_remaining = obj._total_tasks - obj._completed_tasks
        if tasks_remaining <= 0:
            return "Завершен"

        forecast = tasks_remaining * obj._avg_time

        total_seconds = int(forecast.total_seconds())
        minutes = (total_seconds % 3600) // 60
        hours = (total_seconds % 86400) // 3600
        days = total_seconds // 86400

        parts = []
        if days > 0:
            parts.append(f"{days}д")
        if hours > 0:
            parts.append(f"{hours}ч")
        if minutes > 0:
            parts.append(f"{minutes}м")

        return " ".join(parts)
