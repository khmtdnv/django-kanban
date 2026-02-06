from django.db import models

from common.models import BaseModel


class Board(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Название доски")
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="boards",
        verbose_name="Проект",
    )

    class Meta(BaseModel.Meta):
        abstract = False
        verbose_name = "Доска"
        verbose_name_plural = "Доски"

    def __str__(self):
        return self.name
