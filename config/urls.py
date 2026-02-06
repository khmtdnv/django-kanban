from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from apps.boards.router import router as boards_router
from apps.projects.router import router as projects_router
from apps.tasks.router import router as tasks_router

router = routers.DefaultRouter()
router.registry.extend(boards_router.registry)
router.registry.extend(projects_router.registry)
router.registry.extend(tasks_router.registry)


schema_view = get_schema_view(
    openapi.Info(title="Task Manager API", default_version="v1"),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

admin.site.site_header = "Панель управления"
admin.site.site_title = "Admin"
admin.site.index_title = "Добро пожаловать"


urlpatterns = [
    path("", include("django_prometheus.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("api/", include(router.urls)),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger"),
]
if settings.DEBUG:
    urlpatterns.extend(debug_toolbar_urls())
