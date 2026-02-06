from django.conf import settings
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin

from common.models import BaseModel


class Task(ExportModelOperationsMixin("task"), BaseModel):
    class Priority(models.TextChoices):
        LOW = "LOW", "Низкий"
        MEDIUM = "MEDIUM", "Средний"
        HIGH = "HIGH", "Высокий"
        CRITICAL = "CRITICAL", "Критический"

    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Приоритет",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Проект",
    )
    column = models.ForeignKey(
        "boards.Column",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="Колонка",
    )
    sprint = models.ForeignKey(
        "Sprint",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Спринт",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subtasks",
        verbose_name="Родительская задача",
    )

    # Исполнители и метки
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        verbose_name="Исполнитель",
    )
    labels = models.ManyToManyField("Label", blank=True, related_name="tasks")

    estimated_time = models.DurationField("Оценка времени", null=True, blank=True)
    deadline = models.DateTimeField("Дедлайн на основе оценки", null=True, blank=True)
    actual_time = models.DurationField("Затрачено времени", null=True, blank=True)

    class Meta(BaseModel.Meta):
        abstract = False
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["project", "priority"]),
        ]

    def __str__(self):
        return self.name
