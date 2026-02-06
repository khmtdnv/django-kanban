from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 10


class BaseViewSet(viewsets.ModelViewSet):
    """
    Вьюсет с методами `create()`, `retrieve()`, `update()`, `destroy()` and `list()`
    """

    pagination_class = StandardResultsSetPagination
    http_method_names = ["get", "post", "put", "delete", "head", "options", "trace"]

    @swagger_auto_schema(auto_schema=None)  # type: ignore
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)  # type: ignore
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)  # type: ignore
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)  # type: ignore
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)  # type: ignore
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
