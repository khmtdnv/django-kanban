from datetime import datetime

from django.contrib import admin
from django.db.models import Count, Q
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

from .models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):

    list_display = ("name", "project", "total_tasks", "active_tasks", "past_deadline")
    list_filter = ("project",)
    fields = ("name",)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _total_tasks=Count("project__tasks", distinct=True),
            _active_tasks=Count(
                "project__tasks",
                filter=~Q(project__tasks__column__name="Завершено")
                & Q(project__tasks__actual_time__isnull=True),
                distinct=True,
            ),
            _past_deadline=Count(
                "project__tasks",
                filter=Q(project__tasks__deadline__lt=datetime.now())
                & Q(project__tasks__actual_time__isnull=True),
                distinct=True,
            ),
        )
        return queryset

    @admin.display(description="Всего задач", ordering="_total_tasks")
    def total_tasks(self, obj):
        return obj._total_tasks

    @admin.display(description="Активных задач", ordering="_active_tasks")
    def active_tasks(self, obj):
        return obj._active_tasks

    @admin.display(description="Просроченных задач", ordering="_past_deadline")
    def past_deadline(self, obj):
        return obj._past_deadline
