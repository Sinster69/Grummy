from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryTaskViewSet, task_list, complete_task, delete_task

router = DefaultRouter()
router.register("delivery-tasks", DeliveryTaskViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("tasks/", task_list, name="task-list"),
    path("tasks/complete/<int:task_id>/", complete_task, name="complete-task"),
    path("tasks/delete/<int:task_id>/", delete_task, name="delete-task"),
]
