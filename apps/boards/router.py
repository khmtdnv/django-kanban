from rest_framework import routers

from .views import BoardViewSet

router = routers.DefaultRouter()
router.register(r"boards", BoardViewSet, basename="board")
