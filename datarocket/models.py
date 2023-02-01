import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

class customUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stripe_id = models.CharField(max_length=200, blank=True)
    stripe_subscription_id = models.CharField(max_length=200, blank=True)
    stripe_plan_active = models.BooleanField(default=False)
    stripe_plan_id = models.CharField(max_length=200, blank=True)


class endpoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(customUser, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, blank=True)
    url = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

class push(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(customUser, on_delete=models.CASCADE)
    endpoint = models.ForeignKey(endpoint, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    json_file = models.FileField(upload_to="temp/")
    workers = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)

class batch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    push = models.ForeignKey(push, on_delete=models.CASCADE)
    json = models.TextField()
    completed = models.BooleanField(default=False)
    status = models.CharField(max_length=200, blank=True)
    status_message = models.TextField(blank=True)
    failed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(blank=True, null=True)


