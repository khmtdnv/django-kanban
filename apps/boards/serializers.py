from rest_framework import serializers

from .models import Board, Column


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ("id", "name", "project")
        read_only_fields = ("id", "project")
        extra_kwargs = {
            "name": {"help_text": "Название доски"},
            "project": {"help_text": "Проект к которому привязана доска"},
        }


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = ("id", "name", "board", "order")
        read_only_fields = ("id", "board", "order")


class ReorderSerializer(serializers.Serializer):
    ordered_column_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        help_text="Список ID колонок",
    )
