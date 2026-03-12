from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from tasks.models import Restaurant


class Post(models.Model):

    title = models.CharField(max_length=100)

    content = models.TextField()

    date_posted = models.DateTimeField(default=timezone.now)

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.title
