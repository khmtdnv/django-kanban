from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "name", "description", "owner", "members")
        read_only_fields = ("id", "owner", "members")
        extra_kwargs = {
            "name": {"help_text": "Название проекта"},
            "description": {"help_text": "Описание проекта"},
            "owner": {"help_text": "Владелец проекта"},
            "members": {"help_text": "Участники проекта"},
        }


class ProjectAddMembersSerializer(serializers.Serializer):
    member_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=1,
        help_text="Список ID участников",
    )


class ProjectRemoveMemberSerializer(serializers.Serializer):
    member_id = serializers.IntegerField(min_value=1, help_text="ID участника")
