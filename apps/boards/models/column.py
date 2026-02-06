from django.db import models

from common.models import BaseModel


class Column(BaseModel):
    name = models.CharField(
        max_length=255,
        verbose_name="Название колонки",
        default="Новые задачи",
    )
    board = models.ForeignKey(
        "boards.Board",
        on_delete=models.CASCADE,
        related_name="columns",
        verbose_name="Доска",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta(BaseModel.Meta):
        abstract = False
        verbose_name = "Колонка"
        verbose_name_plural = "Колонки"
        ordering = ["order"]
        unique_together = ("board", "order")

    def __str__(self):
        return self.name
