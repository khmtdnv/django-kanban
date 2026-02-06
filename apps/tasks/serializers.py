from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.boards.models import Column
from apps.tasks.models import Task

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "name",
            "description",
            "priority",
            "project",
            "column",
            "sprint",
            "parent",
            "assignee",
            "labels",
            "estimated_time",
            "actual_time",
        )
        read_only_fields = ("id", "project")
        extra_kwargs = {
            "name": {"help_text": "Название"},
            "description": {
                "help_text": "Описание",
            },
            "priority": {"help_text": "Приоритет"},
            "project": {"help_text": "Проект"},
            "column": {"help_text": "Колонка"},
            "sprint": {"help_text": "Спринт"},
            "parent": {"help_text": "Родительская задача"},
            "assignee": {"help_text": "Исполнитель"},
            "labels": {"help_text": "Метки"},
            "estimated_time": {"help_text": "Расчетное время"},
            "actual_time": {"help_text": "Затраченное время"},
        }


class ColumnSerializer(serializers.Serializer):
    column = serializers.PrimaryKeyRelatedField(queryset=Column.objects.all())


class AssigneeSerializer(serializers.Serializer):
    assignee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
