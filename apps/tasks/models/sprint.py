from django.db import models
from django_prometheus.models import ExportModelOperationsMixin

from common.models import BaseModel


class Sprint(ExportModelOperationsMixin("sprint"), BaseModel):
    name = models.CharField(max_length=50, verbose_name="Название")
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="sprints",
        verbose_name="Проект",
    )
    start_date = models.DateField(verbose_name="Начало")
    end_date = models.DateField(verbose_name="Конец")

    class Meta(BaseModel.Meta):
        abstract = False
        verbose_name = "Спринт"
        verbose_name_plural = "Спринты"

    def __str__(self):
        return self.name
