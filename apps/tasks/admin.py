from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter
from django.db.models import (
    BooleanField,
    Case,
    Q,
    Value,
    When,
)
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils import timezone

from .models import Task


class OverdueFilter(admin.SimpleListFilter):
    title = "Статус дедлайна"
    parameter_name = "is_overdue"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Просрочены"),
            ("no", "В срок"),
        )

    def queryset(self, request, queryset):
        now = timezone.now()

        if self.value() == "yes":
            return queryset.filter(deadline__lt=now).exclude(actual_time__isnull=True)
        if self.value() == "no":
            return queryset.filter(Q(deadline__gt=now) | Q(estimated_time__isnull=True))

        return queryset


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "priority",
        "project",
        "column",
        "assignee",
        "estimated_time",
        "actual_time",
        "deadline",
        "past_deadline",
    )
    list_display_links = None
    list_select_related = ("project", "column", "assignee")
    search_fields = (
        "name",
        "priority",
        "project__name",
        "column__name",
        "assignee__phone_number",
    )
    list_filter = (
        ("assignee", RelatedOnlyFieldListFilter),
        "priority",
        ("project", RelatedOnlyFieldListFilter),
        OverdueFilter,
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _past_deadline=Case(
                When(Q(deadline__lt=timezone.now()), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
        )
        return queryset

    @admin.display(description="Просрочена ли задача", ordering="_past_deadline")
    def past_deadline(self, obj):
        return obj._past_deadline
