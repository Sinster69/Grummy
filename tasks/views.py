import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication

from .models import DeliveryTask, Restaurant
from .serializers import DeliveryTaskSerializer
from .tasks import send_task_email

logger = logging.getLogger(__name__)


# ===========================
# API VIEWSET (CACHED)
# ===========================
class DeliveryTaskViewSet(ModelViewSet):

    serializer_class = DeliveryTaskSerializer
    queryset = DeliveryTask.objects.all()

    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cache_key = f"api_tasks_{self.request.user.id}"

        data = cache.get(cache_key)

        if data:
            print("🔥 API CACHE HIT")
        else:
            print("❌ API CACHE MISS")

            restaurant = Restaurant.objects.get(owner=self.request.user)
            queryset = DeliveryTask.objects.filter(restaurant=restaurant)

            data = list(queryset.values())

            cache.set(cache_key, data, timeout=300)  # 5 mins

        return DeliveryTask.objects.filter(id__in=[item["id"] for item in data])

    def perform_create(self, serializer):
        restaurant = Restaurant.objects.get(owner=self.request.user)
        task = serializer.save(restaurant=restaurant)

        # Invalidate cache
        cache.delete(f"api_tasks_{self.request.user.id}")

        logger.info(f"New delivery task created: {task.title} by {self.request.user}")

        send_task_email.delay(self.request.user.email, task.title)


# ===========================
# TEMPLATE VIEW (CACHED)
# ===========================
@login_required
def task_list(request):

    restaurant, created = Restaurant.objects.get_or_create(
        owner=request.user, defaults={"name": f"{request.user.username}'s Restaurant"}
    )

    cache_key = f"task_list_{request.user.id}"
    print(f"Using cache key: {cache_key}")

    # CREATE TASK
    if request.method == "POST":
        task = DeliveryTask.objects.create(
            title=request.POST["title"],
            description=request.POST["description"],
            restaurant=restaurant,
            customer=request.user,
        )

        send_task_email.delay(request.user.email, task.title)

        # Invalidate cache
        cache.delete(cache_key)

        return redirect("task-list")

    # GET TASKS (CACHE)
    tasks = cache.get(cache_key)

    if tasks:
        print("🔥 WEB CACHE HIT")
    else:
        print("❌ WEB CACHE MISS - Fetching from DB")

        tasks = list(DeliveryTask.objects.filter(restaurant=restaurant).values())

        cache.set(cache_key, tasks, timeout=300)  # 5 mins

    return render(request, "tasks/task_list.html", {"tasks": tasks})


# ===========================
# COMPLETE TASK
# ===========================
@login_required
def complete_task(request, task_id):

    restaurant = Restaurant.objects.get(owner=request.user)

    task = DeliveryTask.objects.get(id=task_id, restaurant=restaurant)

    task.status = "completed"
    task.save()

    # Invalidate cache
    cache.delete(f"task_list_{request.user.id}")

    logger.info(f"Task completed: {task.title}")

    return redirect("task-list")


# ===========================
# DELETE TASK
# ===========================
@login_required
def delete_task(request, task_id):

    restaurant = Restaurant.objects.get(owner=request.user)

    task = DeliveryTask.objects.get(id=task_id, restaurant=restaurant)

    task.delete()

    # Invalidate cache
    cache.delete(f"task_list_{request.user.id}")

    logger.info(f"Task deleted: {task.title}")

    return redirect("task-list")
