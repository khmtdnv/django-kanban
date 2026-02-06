from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.services import (
    AssignService,
    TaskCreationService,
    TaskDeletionService,
    TaskMoveService,
    TaskUpdateService,
)
from common.utils import extract_project
from common.viewsets import BaseViewSet

from .models import Task
from .serializers import AssigneeSerializer, ColumnSerializer, TaskSerializer


class TaskViewSet(BaseViewSet):
    serializer_class = TaskSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):  # type: ignore
        return (
            Task.objects.select_related("project", "column", "assignee")
            .prefetch_related("labels")
            .filter(
                Q(project__members=self.request.user)
                | Q(project__owner=self.request.user)
            )
            .distinct()
        )

    @swagger_auto_schema(operation_summary="Список задач")
    def list(self, request, *args, **kwargs):
        project = extract_project(request, type="queryparams")
        queryset = self.get_queryset().filter(project=project)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(operation_summary="Создание задачи")
    def create(self, request, *args, **kwargs):
        project = extract_project(request, type="body")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = TaskCreationService(project, serializer.validated_data)
        created_task = service.execute()
        return Response(
            self.get_serializer(created_task).data,
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(operation_summary="Детали задачи")
    def retrieve(self, request, *args, **kwargs):
        project = extract_project(request, type="queryparams")
        task = get_object_or_404(self.get_queryset(), pk=kwargs["pk"], project=project)
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @swagger_auto_schema(operation_summary="Обновление задачи")
    def update(self, request, *args, **kwargs):
        project = extract_project(request, type="body")
        task = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = TaskUpdateService(project, task, serializer.validated_data)
        updated_task = service.execute()
        return Response(
            self.get_serializer(updated_task).data,
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(operation_summary="Удаление задачи")
    def destroy(self, request, *args, **kwargs):
        project = extract_project(request, type="body")
        task = self.get_object()
        service = TaskDeletionService(project, task)
        service.execute()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(operation_summary="Перемещение задачи между колонками")
    @action(detail=True, methods=["post"], url_path="move")
    def move_task(self, request, pk=None):
        project = extract_project(request, type="body")
        task = self.get_object()
        serializer = ColumnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = TaskMoveService(project, task, serializer.validated_data["column"])
        updated_task = service.execute()

        return Response(self.get_serializer(updated_task).data)

    @swagger_auto_schema(operation_summary="Назначение исполнителя")
    @action(detail=True, methods=["post"], url_path="assign")
    def assign(self, request, pk=None):
        project = extract_project(request, type="body")
        task = self.get_object()
        serializer = AssigneeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = AssignService(project, task, serializer.validated_data["assignee"])
        updated_task = service.execute()

        return Response(self.get_serializer(updated_task).data)

    @swagger_auto_schema(operation_summary="Создание подзадачи")
    @action(detail=True, methods=["post"], url_path="subtasks")
    def create_subtask(self, request, pk=None):
        project = extract_project(request, type="body")
        parent_task = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        creation_service = TaskCreationService(project, serializer.validated_data)
        subtask = creation_service.execute(parent=parent_task)

        return Response(
            self.get_serializer(subtask).data, status=status.HTTP_201_CREATED
        )
