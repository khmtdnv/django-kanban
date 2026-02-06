from django.conf import settings
from django.db import models

from common.models import BaseModel


class Comment(BaseModel):
    task = models.ForeignKey(
        "Task",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Задача",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    text = models.TextField(verbose_name="Текст")
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="mentions",
        blank=True,
        verbose_name="Упомянутые пользователи",
    )

    class Meta(BaseModel.Meta):
        abstract = False
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]
