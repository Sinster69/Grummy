from django.db import models
from django.contrib.auth.models import User


class Restaurant(models.Model):

    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=200)

    address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class DeliveryTask(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()

    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="restaurant_tasks"
    )

    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="customer_tasks"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
