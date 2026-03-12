from django.contrib import admin
from .models import DeliveryTask, Restaurant

admin.site.register(Restaurant)
admin.site.register(DeliveryTask)
