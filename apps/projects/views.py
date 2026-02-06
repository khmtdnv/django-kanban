import time

from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.services import (
    ProjectAddMembersService,
    ProjectCreationService,
    ProjectDeletionService,
    ProjectRemoveMemberService,
    ProjectUpdateService,
)
from common.utils import cache_response
from common.viewsets import BaseViewSet

from .models import Project
from .serializers import (
    ProjectAddMembersSerializer,
    ProjectRemoveMemberSerializer,
    ProjectSerializer,
)


class ProjectViewSet(BaseViewSet):
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):  # type: ignore
        current_user = self.request.user
        time.sleep(10)
        return (
            Project.objects.select_related("owner")
            .prefetch_related("members")
            .filter(owner=current_user)
        )

    @cache_response(ttl=60)
    @swagger_auto_schema(operation_summary="Список проектов")
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(operation_summary="Создание проекта")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = ProjectCreationService(request.user, serializer.data)
        created_project = service.execute()
        return Response(
            self.get_serializer(created_project).data,
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(operation_summary="Детали проекта")
    def retrieve(self, request, *args, **kwargs):
        project = self.get_object()
        serializer = self.get_serializer(project)
        return Response(serializer.data)

    @swagger_auto_schema("Обновление деталей проекта")
    def update(self, request, *args, **kwargs):
        project = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = ProjectUpdateService(project, serializer.validated_data)
        updated_project = service.execute()
        return Response(self.get_serializer(updated_project).data)

    @swagger_auto_schema(operation_summary="Удаление проекта")
    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        service = ProjectDeletionService(project=project)
        service.execute()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(operation_summary="Добавление участников в проект")
    @action(detail=True, methods=["post"], url_path="members")
    def add_members(self, request, pk=None):
        project = self.get_object()
        serializer = ProjectAddMembersSerializer(request.data)
        serializer.is_valid(raise_exception=True)
        validated_member_ids = serializer.validated_data["member_ids"]
        service = ProjectAddMembersService(project, validated_member_ids)
        updated_project = service.execute()

        return Response(
            self.get_serializer(updated_project).data["members"],
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(operation_summary="Удаление участника")
    @action(detail=True, methods=["delete"], url_path="members/(?P<user_id>[^/.]+)")
    def remove_member(self, request, pk=None, user_id=None):
        project = self.get_object()
        url_data = {"member_id": user_id}
        serializer = ProjectRemoveMemberSerializer(data=url_data)
        serializer.is_valid(raise_exception=True)
        service = ProjectRemoveMemberService(project, serializer.validated_data)
        service.execute()

        return Response(status=status.HTTP_204_NO_CONTENT)
