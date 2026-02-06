from django.http import Http404
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import (
    Response,
)
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response: Response | None = exception_handler(exc, context)

    if response is not None:
        view = context.get("view")
        model_name = "Объект"

        if view:
            if hasattr(view, "queryset") and view.queryset is not None:
                model_name = view.queryset.model._meta.verbose_name.capitalize()
            elif hasattr(view, "serializer_class") and view.serializer_class:
                if hasattr(view.serializer_class, "Meta") and hasattr(
                    view.serializer_class.Meta, "model"
                ):
                    model_name = (
                        view.serializer_class.Meta.model._meta.verbose_name.capitalize()
                    )

        if isinstance(exc, Http404):
            response.data = {"detail": f"{model_name} не найден(а)"}

        elif isinstance(exc, PermissionDenied):
            response.data = {
                "detail": "У вас недостаточно прав для выполнения этого действия"
            }

        response.data.setdefault("code", str(response.status_code))  # type: ignore

    return response
