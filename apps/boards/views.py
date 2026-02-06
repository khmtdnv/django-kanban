from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from common.services import (
    BoardCreationService,
    BoardDeletionService,
    BoardUpdateService,
    ColumnCreationService,
    ColumnReorderService,
    ColumnUpdateService,
)
from common.utils import extract_project
from common.viewsets import BaseViewSet

from .models import Board, Column
from .serializers import (
    BoardSerializer,
    ColumnSerializer,
    ReorderSerializer,
)

# from rest_framework.throttling import UserRateThrottle


class BoardViewSet(BaseViewSet):
    serializer_class = BoardSerializer

    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (OrderingFilter,)
    ordering = ("-id",)
    ordering_fields = ("id", "name")

    def get_queryset(self):  # type: ignore
        return (
            Board.objects.select_related("project")
            .filter(
                Q(project__members=self.request.user)
                | Q(project__owner=self.request.user)
            )
            .distinct()
        )

    @swagger_auto_schema(operation_summary="Список досок проекта")
    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        project = extract_project(request, type="queryparams")
        queryset = self.get_queryset().filter(project=project)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(operation_summary="Создание доски в проекте")
    def create(self, request, *args, **kwargs):
        project = extract_project(request, type="body")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = BoardCreationService(project, serializer.validated_data)
        created_board = service.execute()
        return Response(
            self.get_serializer(created_board).data,
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(operation_summary="Обновление доски")
    def update(self, request, *args, **kwargs):
        project = extract_project(request, type="body")
        board = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = BoardUpdateService(board, serializer.validated_data, project)
        updated_board = service.execute()
        return Response(
            self.get_serializer(updated_board).data,
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(operation_summary="Удаление доски")
    def destroy(self, request, *args, **kwargs):
        project = extract_project(request, type="body")
        board = self.get_object()
        service = BoardDeletionService(board, project)
        service.execute()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(operation_summary="Добавление колонки в доску")
    @action(detail=True, methods=["post"], url_path="columns", url_name="add-column")
    def add_column(self, request, pk=None):
        project = extract_project(request, type="body")
        board = self.get_object()
        serializer = ColumnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = ColumnCreationService(board, serializer.validated_data, project)
        created_column = service.execute()
        return Response(
            ColumnSerializer(created_column).data,
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(operation_summary="Обновление колонки")
    @action(detail=True, methods=["put"], url_path="columns/(?P<column_id>[^/.]+)")
    def update_column(self, request, pk=None, column_id=None):
        project = extract_project(request, type="body")
        board = self.get_object()
        column = get_object_or_404(Column, id=column_id, board=board)
        serializer = ColumnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = ColumnUpdateService(column, serializer.validated_data, project)
        updated_column = service.execute()
        return Response(
            ColumnSerializer(updated_column).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="columns/reorder")
    def reorder(self, request, pk=None):
        project = extract_project(request, type="body")
        board = self.get_object()

        serializer = ReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ordered_ids = serializer.validated_data["ordered_column_ids"]

        service = ColumnReorderService(board, ordered_ids, project)
        reordered_columns = service.execute()

        return Response(
            ColumnSerializer(reordered_columns, many=True).data,
            status=status.HTTP_200_OK,
        )
