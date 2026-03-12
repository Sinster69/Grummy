import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication

from .models import DeliveryTask, Restaurant
from .serializers import DeliveryTaskSerializer

logger = logging.getLogger(__name__)


class DeliveryTaskViewSet(ModelViewSet):

    serializer_class = DeliveryTaskSerializer
    queryset = DeliveryTask.objects.all()  # ADD THIS BACK

    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant = Restaurant.objects.get(owner=self.request.user)
        return DeliveryTask.objects.filter(restaurant=restaurant)

    def perform_create(self, serializer):
        restaurant = Restaurant.objects.get(owner=self.request.user)
        task = serializer.save(restaurant=restaurant)

        logger.info(f"New delivery task created: {task.title} by {self.request.user}")


@login_required
def task_list(request):

    restaurant, created = Restaurant.objects.get_or_create(
        owner=request.user, defaults={"name": f"{request.user.username}'s Restaurant"}
    )

    if request.method == "POST":
        DeliveryTask.objects.create(
            title=request.POST["title"],
            description=request.POST["description"],
            restaurant=restaurant,
            customer=request.user,
        )

    tasks = DeliveryTask.objects.filter(restaurant=restaurant)

    return render(request, "tasks/task_list.html", {"tasks": tasks})


@login_required
def complete_task(request, task_id):

    restaurant = Restaurant.objects.get(owner=request.user)

    task = DeliveryTask.objects.get(id=task_id, restaurant=restaurant)

    task.status = "completed"
    task.save()

    logger.info(f"Task completed: {task.title}")

    return redirect("task-list")


@login_required
def delete_task(request, task_id):

    restaurant = Restaurant.objects.get(owner=request.user)

    task = DeliveryTask.objects.get(id=task_id, restaurant=restaurant)

    task.delete()

    logger.info(f"Task deleted: {task.title}")

    return redirect("task-list")
