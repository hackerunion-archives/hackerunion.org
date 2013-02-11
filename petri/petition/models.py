from django.db import models
from django.conf import settings


class Petition(models.Model):
    email = models.EmailField()
    postal_code = models.CharField(max_length=settings.POSTAL_CODE_MAX_LEN)
