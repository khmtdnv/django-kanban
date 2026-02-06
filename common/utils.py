from functools import wraps

from django.core.cache import cache
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from apps.projects.models import Project
from apps.projects.serializers import ProjectSerializer


def extract_project(request: Request, type: str) -> Project:
    current_user = request.user
    if type == "body":
        project_id = request.data.get("project")  # type: ignore
    elif type == "queryparams":
        project_id = request.query_params.get("project")
    else:
        raise ValueError(f"Такой тип не принимается: {type}")

    if not project_id:
        raise ValidationError({"project_id": "ID проекта обязателен"})

    try:
        project_id = int(project_id)
    except (ValueError, TypeError):
        raise ValidationError({"project_id": "Некорректный ID проекта"})

    try:
        project = get_object_or_404(Project, pk=project_id)
    except Http404:
        raise ValidationError({"project": "Такого проекта еще нет"})

    is_owner = project.owner == current_user
    is_member = project.members.filter(id=current_user.id).exists()

    if not (is_owner or is_member):
        raise PermissionDenied("Вы не являетесь участником этого проекта")

    return project


def cache_response(ttl=3600):
    def decorator(view):
        @wraps(view)
        def wrapper(view_instance, request, *args, **kwargs):
            user_id = request.user.id if request.user.is_authenticated else "anon"
            page = request.query_params.get("page", 1)
            cache_key = get_projects_list_cache_key(user_id, page)

            data = cache.get(cache_key)
            if data:
                return Response(data)

            response = view(view_instance, request, *args, **kwargs)

            if hasattr(response, "data"):
                cache.set(cache_key, response.data, timeout=ttl)

            return response

        return wrapper

    return decorator


def get_projects_list_cache_key(user_id, page=1):
    return f"projects:list:user_{user_id}:page_{page}"


def get_user_projects_list(user):
    queryset = (
        Project.objects.select_related("owner")
        .prefetch_related("members")
        .filter(owner=user)
    )

    page_size = 10
    page_queryset = queryset[:page_size]

    serializer = ProjectSerializer(page_queryset, many=True)

    return {
        "count": queryset.count(),
        "next": (
            "http://localhost:8000/api/projects/?page=2"
            if queryset.count() > page_size
            else None
        ),
        "previous": None,
        "results": serializer.data,
    }
