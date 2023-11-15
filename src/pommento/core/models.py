import uuid
from django.conf import settings
from django.db import models

# Create your models here.
class Site(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "pommento_auth.User",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=150)

    def __str__(self):
        return self.user.email + ' ' + self.title


class Page(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.slug


class Comment(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    body = models.TextField()
    name = models.CharField(
        null=False, blank=False, max_length=settings.AUTH_USER_NAME_MAX_LENGTH
    )
    email = models.EmailField(max_length=255, null=True, blank=True)
    ip = models.CharField(max_length=16, null=True, blank=True)
    parent = models.BigIntegerField(null=True, blank=True)
    moderator = models.ForeignKey(
        "pommento_auth.User", on_delete=models.CASCADE, null=True, blank=True
    )
    status = models.BooleanField(default=False)
    redact = models.BooleanField(default=False)
    malicious = models.BooleanField(default=False)
    embargo = models.JSONField(default=dict)
    domain_intel = models.JSONField(default=dict)
    url_intel = models.JSONField(default=dict)
    ip_intel = models.CharField(max_length=100, blank=True)
    user_intel_breach= models.CharField(max_length=100, blank=True)
    def __str__(self):
        return f'{self.name}: {self.body}'
    