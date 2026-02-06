from django.db import models

from common.models import BaseModel


class Label(BaseModel):
    name = models.CharField(max_length=50, verbose_name="Название")
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="labels",
        verbose_name="Проект",
    )

    class Meta(BaseModel.Meta):
        abstract = False
        verbose_name = "Метка"
        verbose_name_plural = "Метки"

    def __str__(self):
        return self.name
