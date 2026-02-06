from django.conf import settings
from django.db import models

from common.models import BaseModel


class Project(BaseModel):
    name = models.CharField(max_length=50, verbose_name="Название проекта")
    description = models.TextField(blank=True, verbose_name="Описание проекта")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_projects",
        verbose_name="Владелец проекта",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="assigned_projects",
        blank=True,
        verbose_name="Участники проекта",
    )

    class Meta(BaseModel.Meta):
        abstract = False
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
