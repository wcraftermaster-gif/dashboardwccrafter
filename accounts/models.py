from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='accounts/avatars/', blank=True, null=True)
    website_url = models.URLField(blank=True)

    def __str__(self):
        return self.username